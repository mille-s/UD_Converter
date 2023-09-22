# UD_Converter

## Introduction
This converter takes as input either a *.conllu file with UD annotations and produces a predicate-argument structure. From v1.3.0, it is also possible to start from plain text and run the Stanza parser to produce the UD annotations (see below). The converter can be used to create training material (e.g. for natural language generation tools) or to extract semantics-oriented relations from UD annotations or parses. The first release of the converter (v1.0.0) supports English, French and Spanish UD structures and was developed on UD v2.0-v2.3. The code was first released for the SR'19 shared task.

The primary purpose of this tool is to produce the datasets for the Multilingual Surface Realisation Shared Tasks series (SR’18-20, see http://taln.upf.edu/pages/msr2020-ws/SRST.html). It outputs two types of structures, called shallow (Track 1) and deep (Track 2) structures, aligned with one another via their IDs (see more details below):

- T1 structures: vanilla UD structures in which word order information has been removed and tokens have been lemmatised, i.e. the inputs are unordered dependency trees with lemmatised nodes that contain PoS tags and morphological information as found in the original annotations (see example below).
- T2 structures: abstracted UD structures from which functional words (in particular, auxiliaries, functional prepositions and conjunctions) and surface-oriented morphological information have been removed, and syntax-oriented relations have been replaced by language-independent predicate-argument relations (see example below).

More information can be found in the [SR’18 Data](https://aclanthology.org/W18-6527/) paper and the [SR’18 shared task](https://aclanthology.org/W18-3601/),  [SR’19 shared task](https://aclanthology.org/D19-6301/) and  [SR’20 shared task](https://aclanthology.org/2020.msr-1.1/) papers. 


## Quick instructions to run the converter on COLAB
1. Go to UD_Converter_release.ipynb and open the project in Colab.
2. Run the first cell to download and unzip the working folder.
3. If the input is text (from v1.3.0):
- run the second cell to install the Stanza parser.
- edit the sentences and run the third cell, or upload a file in the *content/Stanza/Inputs* folder; see *Input specifications* below.
- choose the language.
- run the fourth cell to (i) parse the sentences and (ii) copy the output file(s) to the Converter input folder.
or 3. If the input is a UD structure:
- Upload one or more input file(s) to the */content/UD_converter/Inputs* folder; see *Input specifications* below.
4. If needed, edit the parameters on lines 18-76 of the fourth (last) cell; see *Parameters* below.
5. Run the last cell.
6. Gather the outputs in the */content/UD_converter/Outputs* folder (automatically created).

The 4 output subfolders are *Sent* (original sentences as found in UD metadata, if any), *T1* (T1 structures), *T2* (T2 structures), *debug* (time, alignment checks, well-formedness checks and execution trace for T2 conversion).


## Additional instructions to run the converter offline
1. Download and unzip the working folder locally, and create in the same *UD_Converter* folder a file with the contents of the second cell (e.g. a file called converter.py).
2. In the created file, go to each line that contains *# Code for offline usage*, comment the line immediately above it, and uncomment the line immediately after it.
3. Update the paths on lines 22, 25 &nd 27.
4. The rest of the steps are the same as in the Quick instructions above (Step 3 and following).


## Input specifications

Stanza:
1. Input files should be encoded in **UTF-8 without BOM**.
2. Input files should contain one sentence per line.
3. Input files should be uploaded to the */content/Stanza/Inputs* folder.

UD Converter: A sample input structure is provided in */content/UD_Converter/en_test.conllu*.
1. Input files should be encoded in **UTF-8 without BOM**.
2. Input files should have the **.conllu extension** and be in **CoNLL-U format**, with or without metadata (lines starting with '#'); see [CoNLLU Format description](https://universaldependencies.org/format.html).
3. The UD structures shoud follow the specification of the **official [UD treebanks](https://universaldependencies.org/)**.
4. File names in the input folder should **not contain spaces or parentheses**.
5. A 2-letter + underscore prefix [en_, fr_, es_] should be used to indicate the language: e.g. en_ewt-UD.conllu, fr_myfile.conllu; otherwise, by default, the English converter is selected.
6. Input files should be uploaded to the */content/UD_converter/Inputs* folder.

## Parameters

Stanza: Choose the language of the input file.

UD converter: With the provided default parameters, the converter will process the input structure(s) and create T1 and T2 outputs in the */content/UD_converter/out* folder. Note that the T1 and T2 structures will not be fit for the SR setting (see *Specific instructions for creating SR data* below). There are three blocks of parameters:
1. **General parameters**, who don’t need to be edited; it is recommended to use the debug mode as it doesn’t require too much time and performs a useful output check.
2. **Conversion parameters**, for establishing (i) whether T1 or T2 outputs are desired, (ii) whether the output nodes should be scrambled or not, (iii) what word-order-related information is kept in the T1/T2 outputs, and (iv) if the the outputs have training or test specifications (test has less info).
3. **Additional parameters for T2 conversion**, for establishing which features and nodes are kept or not in the T2 output.

## Specific instructions for creating SR data
1. To get **T1 structures only**: run conversion with track = 't1' parameter and recommended SRST parameter values.
2. To get **T2 structures only**: run conversion with track = 't2' parameter and recommended SRST parameter values; ignore the generated T1 outputs.
3. To get **T1 and T2 structures fully aligned**:
	- run first the conversion with track = ‘t2’ and keep_deep = ‘no’.
	- run the conversion again but this time with track = ‘t1’ and keep_deep = ‘yes’.
	- make sure the alignments between the files are correct and the structures are well formed (read the console output or the files in */content/UD_converter/out/debug*).
4. To get structures in **training mode**: use dt = '1' parameter; to get structures in **test mode**: use dt = '2' parameter.
5. If output templates are needed, run separately create_output_templates.py after updating the datasets in the code.

## Sample structure screenshots
The structures for T1 and T2 are connected trees; the data has the same columns as the original CoNLL-U format; however, the reference sentences can only be found in the original UD data. In the figures below, tabs were added manually to impove the readability of the structures.

**Sample original UD structure for English**

![en_UD.conllu](https://user-images.githubusercontent.com/29705940/203811004-321b8e04-6b3b-4634-9820-66180b317c05.png)


**Sample T1 structure for English (training)**: the nodes of the structure were scrambled.

![en_T1-train.conllu](https://user-images.githubusercontent.com/29705940/203811035-02322b9c-3d46-489f-9de3-2d495eaae3fc.png)


**Sample T1 structure for English (test)**: the nodes of the structure were scrambled, the alignments with the surface tokens are not provided.

![en_T1-test.conllu](https://user-images.githubusercontent.com/29705940/203811049-6e472ad2-56a6-4703-a4d1-cdc04ead696f.png)


**Sample T2 structure for English (training)**: the nodes of the structure were scrambled; the nodes of the Track 2 structures are aligned with the nodes of the Track 1 structures through the attributes id1, id2, id3, etc. Each node can correspond to 0 to 6 superficial nodes; multiple node correspondences involve in particular dependents with the auxiliary, case, det, or cop relations.

![en_T2-train.conllu](https://user-images.githubusercontent.com/29705940/203811069-8fed8d16-7aa6-4bff-acf2-ef3241accc53.png)


**Sample T2 structure for English (test)**: the nodes of the structure were scrambled; the alignments with the surface and Track 1 tokens are not provided.

![en_T2-test.conllu](https://user-images.githubusercontent.com/29705940/203811084-1c78a306-f4da-496f-8aa2-f5ddab1e1f97.png)


**Special features highlight**: Two features were added to store information about relative linear order with respect to the governor (lin), and alignments with the original structures (original_id, in the training data only)

![sample_feats](https://user-images.githubusercontent.com/29705940/203811099-e5e68fdf-402d-47f5-9bcb-8d0aa81041b5.png)
