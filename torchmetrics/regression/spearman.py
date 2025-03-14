# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Any, Dict, List, Optional

import torch
from torch import Tensor

from torchmetrics.functional.regression.spearman import _spearman_corrcoef_compute, _spearman_corrcoef_update
from torchmetrics.metric import Metric
from torchmetrics.utilities import rank_zero_warn
from torchmetrics.utilities.data import dim_zero_cat


class SpearmanCorrCoef(Metric):
    r"""
    Computes `spearmans rank correlation coefficient`_.

    .. math:
        r_s = = \frac{cov(rg_x, rg_y)}{\sigma_{rg_x} * \sigma_{rg_y}}

    where rg_x and rg_y are the rank associated to the variables x and y. Spearmans correlations coefficient
    corresponds to the standard pearsons correlation coefficient calculated on the rank variables.

    Args:
        compute_on_step:
            Forward only calls ``update()`` and returns None if this is set to False.

            .. deprecated:: v0.8
                Argument has no use anymore and will be removed v0.9.

        kwargs:
            Additional keyword arguments, see :ref:`Metric kwargs` for more info.

    Example:
        >>> from torchmetrics import SpearmanCorrCoef
        >>> target = torch.tensor([3, -0.5, 2, 7])
        >>> preds = torch.tensor([2.5, 0.0, 2, 8])
        >>> spearman = SpearmanCorrCoef()
        >>> spearman(preds, target)
        tensor(1.0000)

    """
    is_differentiable = False
    higher_is_better = True
    preds: List[Tensor]
    target: List[Tensor]

    def __init__(
        self,
        compute_on_step: Optional[bool] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        super().__init__(compute_on_step=compute_on_step, **kwargs)
        rank_zero_warn(
            "Metric `SpearmanCorrcoef` will save all targets and predictions in the buffer."
            " For large datasets, this may lead to large memory footprint."
        )

        self.add_state("preds", default=[], dist_reduce_fx="cat")
        self.add_state("target", default=[], dist_reduce_fx="cat")

    def update(self, preds: Tensor, target: Tensor) -> None:  # type: ignore
        """Update state with predictions and targets.

        Args:
            preds: Predictions from model
            target: Ground truth values
        """
        preds, target = _spearman_corrcoef_update(preds, target)
        self.preds.append(preds)
        self.target.append(target)

    def compute(self) -> Tensor:
        """Computes spearmans correlation coefficient."""
        preds = dim_zero_cat(self.preds)
        target = dim_zero_cat(self.target)
        return _spearman_corrcoef_compute(preds, target)
