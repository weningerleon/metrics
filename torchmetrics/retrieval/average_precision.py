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
from torch import Tensor, tensor

from torchmetrics.functional.retrieval.average_precision import retrieval_average_precision
from torchmetrics.retrieval.base import RetrievalMetric


class RetrievalMAP(RetrievalMetric):
    """Computes `Mean Average Precision`_.

    Works with binary target data. Accepts float predictions from a model output.

    Forward accepts

    - ``preds`` (float tensor): ``(N, ...)``
    - ``target`` (long or bool tensor): ``(N, ...)``
    - ``indexes`` (long tensor): ``(N, ...)``

    ``indexes``, ``preds`` and ``target`` must have the same dimension.
    ``indexes`` indicate to which query a prediction belongs.
    Predictions will be first grouped by ``indexes`` and then `MAP` will be computed as the mean
    of the `Average Precisions` over each query.

    Args:
        empty_target_action:
            Specify what to do with queries that do not have at least a positive ``target``. Choose from:

            - ``'neg'``: those queries count as ``0.0`` (default)
            - ``'pos'``: those queries count as ``1.0``
            - ``'skip'``: skip those queries; if all queries are skipped, ``0.0`` is returned
            - ``'error'``: raise a ``ValueError``

        ignore_index:
            Ignore predictions where the target is equal to this number.
        compute_on_step:
            Forward only calls ``update()`` and returns None if this is set to False.

            .. deprecated:: v0.8
                Argument has no use anymore and will be removed v0.9.

        kwargs:
            Additional keyword arguments, see :ref:`Metric kwargs` for more info.

    Raises:
        ValueError:
            If ``empty_target_action`` is not one of ``error``, ``skip``, ``neg`` or ``pos``.
        ValueError:
            If ``ignore_index`` is not `None` or an integer.

    Example:
        >>> from torchmetrics import RetrievalMAP
        >>> indexes = tensor([0, 0, 0, 1, 1, 1, 1])
        >>> preds = tensor([0.2, 0.3, 0.5, 0.1, 0.3, 0.5, 0.2])
        >>> target = tensor([False, False, True, False, True, False, True])
        >>> rmap = RetrievalMAP()
        >>> rmap(preds, target, indexes=indexes)
        tensor(0.7917)
    """

    higher_is_better = True

    def _metric(self, preds: Tensor, target: Tensor) -> Tensor:
        return retrieval_average_precision(preds, target)
