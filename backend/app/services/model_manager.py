"""
Model Manager Service - Centralized loading and management of AI models.

This service handles:
- CLIP for image classification
- BERT/RoBERTa for document classification and NER
- YOLO for object detection
- OpenAI API client for LLM reasoning
- Lazy loading to avoid memory issues
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
from PIL import Image
from transformers import (
    AutoModel,
    AutoTokenizer,
    CLIPModel,
    CLIPProcessor,
)

# YOLO imports
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

# OpenAI imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ModelManager:
    """
    Singleton manager for all AI models.
    Lazy loads models on first use to save memory.
    """

    _instance = None
    _clip_model: Optional[CLIPModel] = None
    _clip_processor: Optional[CLIPProcessor] = None
    _bert_tokenizer: Optional[Any] = None
    _bert_model: Optional[Any] = None
    _yolo_model: Optional[Any] = None
    _device: str = "cuda" if torch.cuda.is_available() else "cpu"

    # Image classification prompts for CLIP
    IMAGE_CLASS_PROMPTS = [
        "a crime scene photograph",
        "a CCTV surveillance camera frame",
        "an injury or medical photograph",
        "a weapon photograph",
        "environmental evidence or location photograph",
    ]

    # Document classification prompts
    DOC_CLASS_PROMPTS = [
        "a witness statement describing events",
        "a medical report with injury details",
        "an FIR or charge sheet document",
        "a police memo or internal report",
        "a general document or report",
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_clip_model(self) -> Tuple[CLIPModel, CLIPProcessor]:
        """Lazy load CLIP model for image classification."""
        if self._clip_model is None:
            print(f"Loading CLIP model on {self._device}...")
            self._clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self._clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self._clip_model.to(self._device)
            self._clip_model.eval()
            print("CLIP model loaded successfully.")
        return self._clip_model, self._clip_processor

    def get_bert_model(self) -> Tuple[Any, Any]:
        """Lazy load BERT model for document classification and NER."""
        if self._bert_model is None:
            print(f"Loading BERT model on {self._device}...")
            # Using a general-purpose BERT model
            # For production, use a fine-tuned model on legal/crime documents
            model_name = "bert-base-uncased"
            self._bert_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._bert_model = AutoModel.from_pretrained(model_name)
            self._bert_model.to(self._device)
            self._bert_model.eval()
            print("BERT model loaded successfully.")
        return self._bert_model, self._bert_tokenizer

    def get_yolo_model(self) -> Optional[Any]:
        """Lazy load YOLO model for object detection."""
        if not YOLO_AVAILABLE:
            print("Warning: ultralytics not installed. YOLO unavailable.")
            return None

        if self._yolo_model is None:
            print(f"Loading YOLO model on {self._device}...")
            # Using YOLOv8n (nano) for faster inference
            # For production, use YOLOv8m or YOLOv8l for better accuracy
            try:
                self._yolo_model = YOLO("yolov8n.pt")
                print("YOLO model loaded successfully.")
            except Exception as e:
                print(f"Warning: Could not load YOLO model: {e}")
                return None
        return self._yolo_model

    def classify_image_clip(self, image_path: Path) -> Dict[str, Any]:
        """
        Classify image using CLIP model.
        Returns: {"label": str, "confidence": float, "all_scores": dict}
        """
        model, processor = self.get_clip_model()

        try:
            image = Image.open(image_path).convert("RGB")
            inputs = processor(
                text=self.IMAGE_CLASS_PROMPTS,
                images=image,
                return_tensors="pt",
                padding=True,
            ).to(self._device)

            with torch.no_grad():
                outputs = model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1).cpu().numpy()[0]

            labels = ["crime_scene", "cctv", "injury", "weapon", "environment"]
            best_idx = np.argmax(probs)
            confidence = float(probs[best_idx])

            all_scores = {labels[i]: float(probs[i]) for i in range(len(labels))}

            return {
                "label": labels[best_idx],
                "confidence": confidence,
                "all_scores": all_scores,
            }
        except Exception as e:
            print(f"CLIP classification error: {e}")
            return {"label": "environment", "confidence": 0.5, "all_scores": {}}

    def classify_document_bert(self, text: str) -> Dict[str, Any]:
        """
        Classify document using BERT embeddings and similarity to category prompts.
        Returns: {"label": str, "confidence": float}
        """
        model, tokenizer = self.get_bert_model()

        try:
            # Quick check: if text doesn't contain crime-related keywords, likely general document
            text_lower = text.lower()
            crime_keywords = ["crime", "suspect", "victim", "police", "arrest", "incident", "assault", 
                            "robbery", "theft", "murder", "investigation", "witness statement", 
                            "medical report", "injury", "fir", "first information report"]
            has_crime_keywords = any(keyword in text_lower for keyword in crime_keywords)
            
            # Get embeddings for document text
            doc_inputs = tokenizer(
                text[:512],  # BERT limit
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            ).to(self._device)

            with torch.no_grad():
                doc_outputs = model(**doc_inputs)
                doc_embedding = doc_outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]

            # Get embeddings for category prompts
            prompt_embeddings = []
            for prompt in self.DOC_CLASS_PROMPTS:
                prompt_inputs = tokenizer(
                    prompt,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=128,
                ).to(self._device)
                with torch.no_grad():
                    prompt_outputs = model(**prompt_inputs)
                    prompt_emb = prompt_outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
                    prompt_embeddings.append(prompt_emb)

            # Compute cosine similarity
            similarities = []
            for prompt_emb in prompt_embeddings:
                sim = np.dot(doc_embedding, prompt_emb) / (
                    np.linalg.norm(doc_embedding) * np.linalg.norm(prompt_emb)
                )
                similarities.append(sim)

            labels = ["witness_statement", "medical_report", "fir", "police_memo", "general_document"]
            best_idx = np.argmax(similarities)
            confidence = float(similarities[best_idx])

            # Normalize confidence to [0, 1] range
            confidence = max(0.0, min(1.0, (confidence + 1) / 2))
            
            # If no crime keywords and best match is crime-related, lower confidence and prefer general_document
            if not has_crime_keywords and labels[best_idx] != "general_document":
                # Check if general_document has reasonable similarity
                general_idx = 4  # general_document index
                general_sim = similarities[general_idx]
                if general_sim > 0.3:  # If general_document is reasonably similar
                    return {
                        "label": "general_document",
                        "confidence": max(0.5, float(general_sim)),
                    }

            return {
                "label": labels[best_idx],
                "confidence": confidence,
            }
        except Exception as e:
            print(f"BERT classification error: {e}")
            return {"label": "general_document", "confidence": 0.5}

    def extract_entities_bert(self, text: str) -> List[Dict[str, str]]:
        """
        Extract named entities using BERT-based NER.
        For production, use a fine-tuned NER model like spaCy's en_core_web_lg
        or a custom BERT-NER model trained on legal documents.
        """
        # Using spaCy as a fallback (more reliable for NER)
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text[:10000])  # Process first 10k chars

            entities = []
            for ent in doc.ents:
                entities.append({
                    "entity": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                })
            return entities
        except Exception as e:
            print(f"Entity extraction error: {e}")
            # Fallback to simple regex-based extraction
            import re
            entities = []
            for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", text[:2000]):
                entities.append({
                    "entity": match.group(1),
                    "label": "PERSON_OR_LOCATION",
                })
            return entities[:50]

    def detect_objects_yolo(self, image_path: Path) -> List[Dict[str, Any]]:
        """
        Detect objects in image using YOLO.
        Returns: List of {"class": str, "confidence": float, "bbox": [x1, y1, x2, y2]}
        """
        model = self.get_yolo_model()
        if model is None:
            return []

        try:
            results = model(str(image_path))
            detections = []

            # YOLO returns results in a specific format
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = model.names[cls_id]

                    # Filter for relevant crime-related objects
                    relevant_classes = [
                        "person", "car", "truck", "motorcycle", "bus",
                        "knife", "gun", "bottle", "backpack", "handbag",
                    ]
                    if class_name in relevant_classes and conf > 0.3:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        detections.append({
                            "class": class_name,
                            "confidence": conf,
                            "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        })

            return detections
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return []

    def llm_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
    ) -> str:
        """
        Call OpenAI API for LLM-based reasoning.
        Uses settings.openai_api_key from config (loaded from .env file).
        """
        from app.config import settings
        
        if not OPENAI_AVAILABLE:
            print("⚠️ LLM reasoning unavailable: openai package not installed.")
            return "LLM reasoning unavailable: openai package not installed."

        # Use API key from settings (loaded from .env)
        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "" or api_key == "your_openai_api_key_here":
            print("⚠️ LLM reasoning unavailable: OPENAI_API_KEY not set in .env file.")
            print("   Please add OPENAI_API_KEY=sk-... to backend/.env")
            return "LLM reasoning unavailable: OPENAI_API_KEY not set."

        try:
            print(f"🤖 Calling OpenAI API with model: {model}")
            print(f"   Prompt length: {len(prompt)} chars")
            client = openai.OpenAI(api_key=api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000,
            )
            result = response.choices[0].message.content
            print(f"✅ OpenAI API response received ({len(result)} chars)")
            return result
        except Exception as e:
            error_msg = f"LLM reasoning error: {e}"
            print(f"❌ {error_msg}")
            return error_msg


# Global singleton instance
model_manager = ModelManager()

