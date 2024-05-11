import torch
from torchvision.transforms import Normalize
import torch.nn.functional as F
from torch import nn
from torchvision import transforms
from PIL import Image
import numpy as np
from keras.models import Model
from keras.layers import Dropout, Dense
from keras.saving import load_model
from keras.applications.mobilenet import preprocess_input, MobileNet
from keras.preprocessing.image import img_to_array, load_img

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 16 * 16, 128)
        self.fc2 = nn.Linear(128, 1)


    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv3(x))
        x = F.max_pool2d(x, 2)

        x = x.view(-1, 64 * 16 * 16)

        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


@st.cache
def load_cnn_model():
    cnn = CNN()
    return cnn.load_state_dict(torch.load("Models/cnn_model.pth"))


@st.cache
def load_mn_model():
    return load_model("Models/mn_model.keras")


cnn = load_cnn_model()
MN_model = load_mn_model()

nima = MobileNet((None, None, 3), alpha=1, include_top=False, pooling='avg', weights=None)
x = Dropout(0.75)(nima.output)
x = Dense(10, activation='softmax')(x)
nima = Model(nima.input, x)
nima.load_weights('Models/nima_model.h5')

def get_cnn_predict(image):
    img = Image.open(image)
    img = img.convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor()
    ])
    image_norm = transform(img)
    pred = cnn(image_norm).item()

    return pred


def nima_pred(img):
    img = img.resize((224, 224))
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    scores = nima.predict(x, batch_size=1, verbose=0)[0]
    return np.sum(scores * np.arange(1, 11, 1))

def mobilenet_pred(image_path):
    img = load_img(image_path, target_size=(224, 224)).convert("RGB")
    img = img_to_array(img) / 255.
    img = img.reshape((1, 224, 224, 3))
    x = MN_model.predict(img)
    x = int(x*100) / 100
    return x
