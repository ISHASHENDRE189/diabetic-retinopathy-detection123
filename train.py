import lightning as L
import torch
from lightning.pytorch.callbacks import (
    ModelCheckpoint,
    LearningRateMonitor,
    EarlyStopping,
)
from lightning.pytorch.loggers import TensorBoardLogger

from src.dataset import DRDataModule
from src.model import DRModel

# seed everything for reproducibility
SEED = 42
L.seed_everything(SEED, workers=True)
torch.set_float32_matmul_precision("high")


# Init DataModule
dm = DRDataModule(batch_size=128, num_workers=24)
dm.setup()

# Init model from datamodule's attributes
model = DRModel(
    num_classes=dm.num_classes, learning_rate=3e-4, class_weights=dm.class_weights
)

# Init logger
logger = TensorBoardLogger(save_dir="artifacts")
# Init callbacks
checkpoint_callback = ModelCheckpoint(
    monitor="val_loss",
    mode="min",
    save_top_k=2,
    dirpath="artifacts/checkpoints",
    filename="{epoch}-{step}-{val_loss:.2f}-{val_acc:.2f}-{val_kappa:.2f}",
)

# Init LearningRateMonitor
lr_monitor = LearningRateMonitor(logging_interval="step")

# early stopping
early_stopping = EarlyStopping(
    monitor="val_loss",
    patience=5,
    verbose=True,
    mode="min",
)

# Init trainer
trainer = L.Trainer(
    max_epochs=20,
    accelerator="auto",
    devices="auto",
    logger=logger,
    callbacks=[checkpoint_callback, lr_monitor, early_stopping],
    # check_val_every_n_epoch=4,
)

# Pass the datamodule as arg to trainer.fit to override model hooks :)
trainer.fit(model, dm)
