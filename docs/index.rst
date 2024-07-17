.. QClab documentation master file, created by
   sphinx-quickstart on Mon Jul 15 16:14:45 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to the QClab documentation!
===================================

**QClab** QClab (pronounced "QC" "lab") is a package for carrying out mixed quantum-classical (MQC) dynamics simulations. 
It implements popular MQC algorithms in a manner that is agnostic to the underlying physical system and flexible to the mixed quantum-classical algorithm. 
Along with several built-in dynamics algorithms, QClab comes with a variety of physical models that can be used as starting points for exploring MQC dynamics 
or to implement more elaborate models. 

Capabilities
------------

Dynamics Algorithms
```````````````````

The following algorithms are implemented making use of the complex-classical coordinate formalism established in [1]. and are formally identical to their original real-space formulation while being invariant to global unitary transformations of the classical and quantum bases. 


* Mean-field (Ehrenfest) dynamics [2]
* Fewest-switches surface hopping (FSSH) dynamics [3]
* Coherent fewest-switches surface hopping (CFSSH) dynamics [4]

Model Systems
`````````````

* Spin-boson model [4]
* Donor-bridge-acceptor model [5]
* Holstein lattice model [6]


Installing QClab
-----------------

QClab can be installed with pip::

   pip install QClab

or from source by downloading the github repository and executing::

   pip install -e ./

from inside its topmost directory. 

Using QClab
-----------

.. toctree::
   :maxdepth: 3
   
   introduction
   making_models

Bibliography

1. Miyazaki, K.; Krotz, A.; Tempelaar, R. Unitary Basis Transformations in Mixed Quantum-Classical Dynamics. arXiv April 23, 2024. http://arxiv.org/abs/2404.15614.
2. Tully, J. C. Mixed Quantum–Classical Dynamics. Faraday Discuss. 1998, 110 (0), 407–419. https://doi.org/10.1039/A801824C.
3. Hammes‐Schiffer, S.; Tully, J. C. Proton Transfer in Solution: Molecular Dynamics with Quantum Transitions. J. Chem. Phys. 1994, 101 (6), 4657–4667. https://doi.org/10.1063/1.467455.
4. Tempelaar, R.; Reichman, D. R. Generalization of Fewest-Switches Surface Hopping for Coherences. The Journal of Chemical Physics 2018, 148 (10), 102309. https://doi.org/10.1063/1.5000843.
5. Bondarenko, A. S.; Tempelaar, R. Overcoming Positivity Violations for Density Matrices in Surface Hopping. J. Chem. Phys. 2023, 158 (5), 054117. https://doi.org/10.1063/5.0135456.
6. Krotz, A.; Provazza, J.; Tempelaar, R. A Reciprocal-Space Formulation of Mixed Quantum–Classical Dynamics. J. Chem. Phys. 2021, 154 (22), 224101. https://doi.org/10.1063/5.0053177.


Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.






