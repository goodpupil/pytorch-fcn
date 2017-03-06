import torch.nn as nn


class FCN32s(nn.Module):

    def __init__(self, n_class=21, deconv=True):
        super(FCN32s, self).__init__()
        self.use_deconv = deconv
        self.features = nn.Sequential(
            # conv1
            nn.Conv2d(3, 64, 3, padding=100 if deconv else 1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2, ceil_mode=True),  # 1/2

            # conv2
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2, ceil_mode=True),  # 1/4

            # conv3
            nn.Conv2d(128, 256, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2, ceil_mode=True),  # 1/8

            # conv4
            nn.Conv2d(256, 512, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2, ceil_mode=True),  # 1/16

            # conv5
            nn.Conv2d(512, 512, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, stride=2, ceil_mode=True),  # 1/32
        )
        self.classifier = nn.Sequential(
            # fc6
            nn.Conv2d(512, 4096, 7),
            nn.ReLU(inplace=True),
            nn.Dropout2d(),

            # fc7
            nn.Conv2d(4096, 4096, 1),
            nn.ReLU(inplace=True),
            nn.Dropout2d(),

            # score_fr
            nn.Conv2d(4096, n_class, 1),
        )
        if self.use_deconv:
            upscore = nn.ConvTranspose2d(n_class, n_class, 64, stride=32,
                                         bias=False)
        else:
            upscore = nn.UpsamplingBilinear2d(scale_factor=32)
        self.upscore = nn.Sequential(upscore)

    def forward(self, x):
        h = self.features(x)

        h = self.classifier(h)

        if self.use_deconv:
            h = self.upscore(h)
            h = h[:, :, 19:19+x.size()[2], 19:19+x.size()[3]].contiguous()
        else:
            self.upscore[0].size = x.size()[2], x.size()[3]
            h = self.upscore(h)

        return h
