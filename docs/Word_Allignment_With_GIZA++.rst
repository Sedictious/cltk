Word Allignment with GIZA++
===========================

Installing 
----------
You can follow the installation guide `here <https://okapiframework.org/wiki/index.php?title=GIZA%2B%2B_Installation_and_Running_Tutorial>`_. Note that for non Unix-like operating systems, you will need to manually set up your environment ( `Cygwin <https://www.cygwin.com/>`_ being a particularly popular choice for Windows).

Cleaning text
-------------
You will need to compile a bilingual text. I will be using L. D. Benson's interlinear translation of Chaucer's Canterbury Tales found `here <http://sites.fas.harvard.edu/~chaucer/teachslf/tr-index.htm>`_ and cleaned by using CLTK's `normalizer <http://docs.cltk.org/en/latest/middle_english.html#text-normalization>`_. After preprocessing, our two text files should look like this

  whan that aprill with his shoures soote 
  
  the droghte of march hath perced to the roote
  
  and bathed every veyne in swich licour

..

  when april with its sweet-smelling showers
  
  has pierced the drought of march to the root
  
  and bathed every vein of the plants in such liquid
  

Aligning
--------
  
By now, you should have your two files, conventionally named ``original`` (middle english) and ``translation`` (modern english).

Navigate to the directory you extracted GIZA (most likely .\\giza-pp\\GIZA++-v2\\) and run the following command

.. code-block::

  ./plain2snt.out translation original

You should be seeing four new files, ``original.vcb``, ``translation.vcb``, ``original_translation.snt`` and ``tranlation_original.snt``.

The ``snt`` files contain the number encoded sentences, whereas the ``vcb`` suffix reffers to a file containing the frequency of each word along with its unique ID.

Navigate to ``.\\mkcls-v2\\`` and run the following command:

.. code-block::
  
  ./GIZA++ -S original.vcb -T translation.vcb -C original_translation.snt
  
After the training is over, you will find a multitude of new files, only two of which interest you:

``ti.final`` and ``actual.ti.final``.

The former consist of triples of the form (modern_english_word, middle_english_word, probability). Note that any given word can match to NULL.

  impression impression 0.524856
  
  true aright 3.17784e-06
  
  tapestry-maker tapycer 1
  
  bag poke 0.166666
  
  turn agayn 0.0557224
  
  again agayn 0.517093


``actual.ti.final`` is nearly identical, the only difference being that instead of words, it uses the IDs assigned in the afforementioned ``.vcb`` files.

