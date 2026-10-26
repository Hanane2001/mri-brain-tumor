import torch

vect1 = torch.tensor([1.0, 2.0, 3.0])
vect2 = torch.tensor([4.0, 5.0, 6.0])
def calculate_vector_dot_product(vect1, vect2):
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        print("GPU n'est pas disponible")
        device = torch.device("cpu")
    if vect1.ndim != 1 or vect2.ndim != 1:
        print("vecteur n'est pas un seul dimension")
    if vect1.size(0) != vect2.size(0):
        print("les deux vects n'est pas en meme size")
    return torch.dot(vect1, vect2)