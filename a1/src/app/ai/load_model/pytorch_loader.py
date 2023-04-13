import sys
import os
import torch

# TODO: hacky, it would be better to fully resolve the import
# paths once we finalize a location for the ai models
from app import app
sys.path.insert(1, os.path.join(app.root_path, 'ai/models'))

def load_pytorch_model(model_path):
    model = torch.load(model_path)
    return model

def pytorch_inference(model, img_arr):
    if torch.cuda.is_available():
        dev = 'cuda:0'
    else:
        dev = 'cpu'
    device = torch.device(dev)
    model.to(device)
    input_tensor = torch.tensor(img_arr).float().to(device)
    y_bboxes, y_scores, = model.forward(input_tensor)
    return y_bboxes.detach().cpu().numpy(), y_scores.detach().cpu().numpy()
