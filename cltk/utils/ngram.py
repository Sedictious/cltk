from collections import defaultdict

from math import exp
from math import log

def ngrams(n, lst, pad_left=False, pad_right=False):
    """"
    Generate ngrams from normalized list

    Examples:
        >>> Sentence  = ['forsan', 'et', 'haec', 'olim', 'meminisse', 'iuvabit']

        >>> ngrams(2, Sentence)
        [['forsan', 'et'], ['et', 'haec'], ['haec', 'olim'], ['olim', 'meminisse'], ['meminisse', 'iuvabit']]

        >>> ngrams(2, Sentence, pad_left=True)
        [['<s>', '<s>'], ['<s>', 'forsan'], ['forsan', 'et'], ['et', 'haec'], ['haec', 'olim'], ['olim', 'meminisse'], ['meminisse', 'iuvabit']]

        >>> ngrams(2, Sentence, pad_right=True)
        [['forsan', 'et'], ['et', 'haec'], ['haec', 'olim'], ['olim', 'meminisse'], ['meminisse', 'iuvabit'], ['iuvabit', '</s>'], ['</s>', '</s>']]
    """

    lst = ['<s>' for _ in range(pad_left*n)] + lst + ['</s>' for _ in range(pad_right*n)]
    return [lst[i:i+n] for i in range(len(lst)-n+1)]


def ngrams_freq(ngramLst):
    """
    :param ngramLst: list of ngrams
    :return:

    Examples:
        >>> Sentence  = ['forsan', 'et', 'haec', 'et', 'haec']

        >>> ngrams_freq(ngrams(2, Sentence, pad_right=True))
        defaultdict(<class 'int'>, {('forsan', 'et'): 1, ('et', 'haec'): 2, ('haec', 'et'): 1, ('haec', None): 1})
    """
    dicts = defaultdict(int)

    for ngram in ngramLst:
        dicts[tuple(ngram)] += 1
    return dicts


class TextProbability:

    def __init__(self, text):
        #For efficiency reasons, at most pentagrams are pre-calculated

        #TO-DO: Implement trees, for space efficiency
        #List of 12345-grams
        self.text_ngrams = [ngrams(i, text, pad_left=True, pad_right=True) for i in range(6)]

        #Count of respective ngrams
        self.text_freq_ngrams = [ngrams_freq(self.text_ngrams[i]) for i in range(6)]

        #Create nested bigram dictionary for fast hashing

        self.nested_bigrams = defaultdict(dict)
        self.inverse_nested_bigrams = defaultdict(dict)

        for u, v in self.text_freq_ngrams[2].items():
            self.inverse_nested_bigrams[u[1]][u[0]] = v
            self.nested_bigrams[u[0]][u[1]] = v

        #Coefficients for linear interpolation model
        self.lerp_lambda = [0, 0.2, 0.2, 0.2, 0.2, 0.2]

    def ngram_interpolation(self, sentence):

        return sum([self.lerp_lambda[i]*exp(self.sentenceP(sentence, n=i)) for i in range(1,6)])

    def katzBackoff(self, sentence, a=1):
        #Return 1 if word hasn't been seen
        if len(sentence) == 1 and self.text_freq_ngrams[1][tuple(sentence)] == 0: return 0
        print(sentence)
        try:
            if self.conditionalP(sentence[-1], sentence[:-1]) > 0:
                return self.conditionalP(sentence[-1], sentence[:-1])*a
            else:
                return a*self.katzBackoff(sentence[2:], a=a)
        except:
            return a*self.katzBackoff(sentence[1:], a=a)

    def stupid_backoff(self, w, h, l):
        if len(h) == 0: return 0

        if self.conditionalP(w, h) > 0:
            return self.conditionalP(w, h)
        return l*self.stupid_backoff(w, h[1:], l)

    def set_lerp_lambda(self, lerp_lambda):
        """
        Sets the new coefficients of linear interpolation.

        :param lerp_lambda: int list:
        """
        if sum(lerp_lambda)!= 1 or len(lerp_lambda)!= 5:
            raise ValueError

        self.lerp_lambda = [0] + lerp_lambda

    def ksmoothing(self, w, h, k=1):
        """
        Calculates the conditional probability P(w|k) applying k-smoothing
        P(w|h) = (C(hw) + k)/(C(h) + kV)

        :param w: str
        :param h: str list
        :param k: int
        """

        return (self.text_freq_ngrams[len(h) + 1][tuple(h + [w])] + k) / \
               ((self.text_freq_ngrams[len(h)][tuple(h)]) + k*len(self.text_ngrams[1]))

    def conditionalP(self, w, h):

        """
        Calculates the conditional probability P(w|h) = C(hw)/C(h),
        where w a word and h an n-gram indicating the context of w.

        :param w: str
        :param h: str list
        """

        try:
            return self.text_freq_ngrams[len(h) + 1][tuple(h + [w])] / \
               (self.text_freq_ngrams[len(h)][tuple(h)])
        except:
            return 0

    def sentenceP(self, sentence, n=2, smoothing=None):
        """
        Calculates the probability of a sentence.

        :param sentence: str list: the input sentence
        :param n: int: The context to be considered (max 5)
        """
        smoothing = self.conditionalP if smoothing is None else smoothing

        return exp(sum([log(smoothing(str(sentence[max(0, i-n):i][-1]), sentence[max(0, i-n):i][:-1]))
                    for i in range(1, len(sentence) + n - 1)]))

    def perplexity(self, sentence, n=2):
        """
        Calculates the perplexity of a sentence for the current language model

        :param sentence: str
        :param n: int
        """
        return self.sentenceP(sentence, n)**(-1/len(sentence))

    def continuationP(self, w):
        """
        Calculates the different context of w:
        |{v: C(vw)>0}|/|{(u, v): C(u, v)>0|

        TO-DO: Use a tree instead of a dictionary to achieve logarithmic
        search speed.

        :param w: str
        """
        return len(self.nested_bigrams[w])/len(self.text_freq_ngrams[2])

    def kneser_ney(self, w, u, d):

        #Calculate normalizing constant
        try: l = d*len(self.inverse_nested_bigrams[u])/sum(self.nested_bigrams[u].values())
        except: l = 0

        try: return max(self.text_freq_ngrams[2][tuple([u,w])] - d, 0)/self.text_freq_ngrams[1][tuple([u])] + l*self.continuationP(w)
        except: return 0
        
        
