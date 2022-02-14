import kindred
from collections import Counter

def test_corpus_split():
	mainCorpus = kindred.Corpus()
	for i in range(100):
		doc = kindred.Document(text=str(i))
		mainCorpus.addDocument(doc)

	corpusA,corpusB = mainCorpus.split(0.75)

	assert len(corpusA.documents) == 75
	assert len(corpusB.documents) == 25

	seen = set()
	for doc in corpusA.documents:
		assert doc in mainCorpus.documents, "This document doesn't match an existing one"
		assert not doc in seen, "This document isn't unique now"
		seen.add(doc)
	for doc in corpusB.documents:
		assert doc in mainCorpus.documents, "This document doesn't match an existing one"
		assert doc not in seen, "This document isn't unique now"
		seen.add(doc)

	assert len(seen) == len(mainCorpus.documents)

def test_corpus_nfold_split():
	mainCorpus = kindred.Corpus()
	docCount = 100
	for i in range(docCount):
		doc = kindred.Document(text=str(i))
		mainCorpus.addDocument(doc)

	corpusA,corpusB = mainCorpus.split(0.75)
	folds = 5
	trainCounter,testCounter = Counter(),Counter()
	seen = set()
	for trainCorpus,testCorpus in mainCorpus.nfold_split(folds):
		assert len(trainCorpus.documents) == (folds-1) * docCount / folds
		assert len(testCorpus.documents) == docCount / folds

		for doc in corpusA.documents:
			assert doc in mainCorpus.documents, "This document doesn't match an existing one"
			assert not doc in seen, "This document isn't unique now"
			trainCounter[doc] += 1
		for doc in corpusB.documents:
			assert doc in mainCorpus.documents, "This document doesn't match an existing one"
			assert doc not in seen, "This document isn't unique now"
			testCounter[doc] += 1

	for doc,count in trainCounter.items():
		assert count == folds
	for doc,count in testCounter.items():
		assert count == folds

def test_corpus_splitIntoSentences():
	text = "<drug id='1'>Erlotinib</drug> is an <gene id='2'>EGFR</gene> inhibitor. <drug id='3'>Gefitinib</drug> is another drug. <relation type='inhibits' drug='1' gene='2' />"
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)

	parser = kindred.Parser()
	parser.parse(corpus)

	sentenceCorpus = corpus.splitIntoSentences()

	assert sentenceCorpus.parsed == True

	assert isinstance(sentenceCorpus,kindred.Corpus)
	assert len(sentenceCorpus.documents) == 2

	expected1 = "<Document Erlotinib is an EGFR inhibitor. [<Entity drug:'Erlotinib' sourceid=1 [(0, 9)]>, <Entity gene:'EGFR' sourceid=2 [(16, 20)]>] [<Relation inhibits [<Entity drug:'Erlotinib' sourceid=1 [(0, 9)]>, <Entity gene:'EGFR' sourceid=2 [(16, 20)]>] ['drug', 'gene']>]>"
	expected2 = "<Document Gefitinib is another drug. [<Entity drug:'Gefitinib' sourceid=3 [(0, 9)]>] []>"

	assert str(sentenceCorpus.documents[0]) == expected1
	assert str(sentenceCorpus.documents[1]) == expected2

	doc0 = sentenceCorpus.documents[0]
	assert len(doc0.sentences) == 1

	sentence0 = doc0.sentences[0]
	expectedTokens0 = "('Erlotinib', 0, 9),('is', 10, 12),('an', 13, 15),('EGFR', 16, 20),('inhibitor', 21, 30),('.', 30, 31)"

	assert ",".join(str((t.word,t.startPos,t.endPos)) for t in sentence0.tokens).replace("u'","'") == expectedTokens0
	assert len(sentence0.dependencies) == 6
	assert str(sentence0.entityAnnotations) == "[(<Entity drug:'Erlotinib' sourceid=1 [(0, 9)]>, [0]), (<Entity gene:'EGFR' sourceid=2 [(16, 20)]>, [3])]"

	doc1 = sentenceCorpus.documents[1]
	assert len(doc1.sentences) == 1

	sentence1 = doc1.sentences[0]
	expectedTokens1 = "('Gefitinib', 0, 9),('is', 10, 12),('another', 13, 20),('drug', 21, 25),('.', 25, 26)"
	assert ",".join(str((t.word,t.startPos,t.endPos)) for t in sentence1.tokens).replace("u'","'") == expectedTokens1
	assert len(sentence1.dependencies) == 5
	assert str(sentence1.entityAnnotations) == "[(<Entity drug:'Gefitinib' sourceid=3 [(0, 9)]>, [0])]"

