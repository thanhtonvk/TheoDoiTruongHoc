from torch import nn
import torchvision.models as models
import torch
import cv2
import numpy as np
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class TimeWarp(nn.Module):
    def __init__(self, baseModel, method='sqeeze'):
        super(TimeWarp, self).__init__()
        self.baseModel = baseModel
        self.method = method

    def forward(self, x):
        batch_size, time_steps, C, H, W = x.size()
        if self.method == 'loop':
            output = []
            for i in range(time_steps):
                # input one frame at a time into the basemodel
                x_t = self.baseModel(x[:, i, :, :, :])
                # Flatten the output
                x_t = x_t.view(x_t.size(0), -1)
                output.append(x_t)
            # end loop
            # make output as  ( samples, timesteps, output_size)
            x = torch.stack(output, dim=0).transpose_(0, 1)
            output = None  # clear var to reduce data  in memory
            x_t = None  # clear var to reduce data  in memory
        else:
            # reshape input  to be (batch_size * timesteps, input_size)
            x = x.contiguous().view(batch_size * time_steps, C, H, W)
            x = self.baseModel(x)
            x = x.view(x.size(0), -1)
            # make output as  ( samples, timesteps, output_size)
            x = x.contiguous().view(batch_size, time_steps, x.size(-1))
        return x
class extractlastcell(nn.Module):
    def forward(self, x):
        out, _ = x
        return out[:, -1, :]

def create_model():

    num_classes = 2
    dr_rate = 0.2
    rnn_hidden_size = 30
    rnn_num_layers = 2
    baseModel = models.mobilenet_v2(weights=None).features
    i = 0
    num_features = 62720
    # Example of using Sequential
    model = nn.Sequential(TimeWarp(baseModel),
                          nn.Dropout(dr_rate),
                          nn.LSTM(num_features, rnn_hidden_size,
                                  rnn_num_layers, batch_first=True),
                          extractlastcell(),
                          nn.Linear(30, 256),
                          nn.ReLU(),
                          nn.Dropout(dr_rate),
                          nn.Linear(256, num_classes), 
                          nn.Softmax(-1))
    model.load_state_dict(torch.load(
        'models/best_model_fine.pth', map_location=device))
    model.to(device)
    model.eval()
    return model
model = create_model()
def predict_baoluc(frame_list):
    frames = []
    for frame in frame_list:
        frm = cv2.resize(frame,(224,224))
        frm = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
        frm = np.moveaxis(frm, -1, 0)
        frames.append(frm)
    frames= np.array(frames).astype(np.float32)
    frames = frames/255.0
    frames = np.expand_dims(frames,0)
    inputs = torch.from_numpy(frames).float().to(device)    
    with torch.no_grad():
        result = model(inputs)
    score=  result.cpu().detach().numpy()[0][1]
    print(score)
    if score>0.999:
        return True
    return False
    
