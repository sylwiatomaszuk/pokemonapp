from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision.models import ResNet18_Weights, resnet18


class CardEmbedder:
    """
    Erzeugt aus einem Kartenbild einen 512-dimensionalen Bildvektor
    mit einem auf ImageNet vortrainierten ResNet18.
    """

    def __init__(self):
        self.weights = ResNet18_Weights.DEFAULT

        # GPU verwenden, falls PyTorch eine CUDA-GPU erkennt.
        # Ansonsten automatisch CPU.
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        model = resnet18(weights=self.weights)

        # Die normale Klassifikationsschicht wird entfernt.
        # Dadurch liefert ResNet18 einen 512D-Feature-Vektor.
        model.fc = torch.nn.Identity()

        self.model = model.to(self.device)
        self.model.eval()

        # Passende Vorverarbeitung für die ImageNet-Gewichte.
        self.transform = self.weights.transforms()

        print(f"ResNet18 läuft auf: {self.device}")

    def get_embedding(self, image_path: str | Path) -> np.ndarray:
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Bild wurde nicht gefunden: {image_path}"
            )

        image = Image.open(image_path).convert("RGB")

        image_tensor = self.transform(image)
        image_tensor = image_tensor.unsqueeze(0).to(self.device)

        with torch.no_grad():
            embedding = self.model(image_tensor)

        # L2-Normalisierung.
        # Dadurch können wir später einfach das Skalarprodukt
        # als Cosine Similarity verwenden.
        embedding = F.normalize(
            embedding,
            p=2,
            dim=1
        )

        return embedding.cpu().numpy()[0].astype(np.float32)