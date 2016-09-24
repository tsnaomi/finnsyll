## FinnSyll

FinnSyll is a Python library that syllabifies words according to Finnish syllabification principles.
It is also equipped with a Finnish compound splitter. 
More details/docs to come.

### Installation

```$ pip install FinnSyll```

### Basic usage

First, instantiate a ```FinnSyll``` object.

```
>>> from finnsyll import FinnSyll
>>> f = FinnSyll()
```

To syllabify:
```
>>> f.syllabify('runoja')
['ru.no.ja']  # internal syllable boundaries are indicated with '.'
```

To segment compounds:
```
>>> f.split('sosiaalidemokraattien')
'sosiaali=demokraattien'  # internal word boundaries are indicated with '='
```

### Optional arguments

The syllabifier can be customized along two different parameters: variation and compound splitting.  

####variation

Instantiating a ```FinnSyll``` object with ```variation=True``` (default) will allow the syllabifier to return multiple syllabifications if variation is predicted. When ```variation=True```, the syllabifier will return a list. Setting ```variation``` to ```False``` will cause the syllabifier to return a string containing the first predicted syllabification. 

*Variation*:
```
>>> f = FinnSyll(variation=True) 
>>> f.syllabify('runoja')
['ru.no.ja']
>>> f.syllabify('vapaus')
['va.pa.us', 'va.paus']
```

*No variation*:
```
>>> f = FinnSyll(variation=False)
>>> f.syllabify('runoja')
'ru.no.ja'
>>> f.syllabify('vapaus')
'va.pa.us'
```

#### split_compounds

When instantiating a ```FinnSyll``` object with ```split_compounds=True``` (default), the syllabifier will first attempt to split the input into constituent words before syllabifying it. This forces the syllabifier to insert a syllable boundary in between identified constituent words. The syllabifier will skip this step if ```split_compounds``` is set to ```False```.

*Compound splitting*:
```
>>> f = FinnSyll(split_compounds=True) 
>>> f.syllabify('rahoituserien')  # rahoitus=erien
['ra.hoi.tus.e.ri.en']
```

*No compound splitting*:
```
>>> f = FinnSyll(split_compounds=False) 
>>> f.syllabify('rahoituserien')
['ra.hoi.tu.se.ri.en']  # incorrect
```
  
