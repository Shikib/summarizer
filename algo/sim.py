import math, string
import re

import numpy as np
from scipy.sparse import csc_matrix

pos_scores = [0.17, 0.23, 0.14, 0.08, 0.05, 0.04, 0.06, 0.04, 0.04, 0.15, 0]
epsilon = 1e-10

def page_rank(G, s = .85, maxerr = .001):
    """
    Computes the pagerank for each of the n states.
    Used in webpage ranking and text summarization using unweighted
    or weighted transitions respectively.
    Args
    ----------
    G: matrix representing state transitions
       Gij can be a boolean or non negative real number representing the
       transition weight from state i to j.
    Kwargs
    ----------
    s: probability of following a transition. 1-s probability of teleporting
       to another state. Defaults to 0.85
    maxerr: if the sum of pageranks between iterations is bellow this we will
            have converged. Defaults to 0.001
    """
    n = len(G[0])
    
    for i in range(0, len(G)):
        column = G[i]
        summ = sum(column)
        for j in range(0, len(G)):
            if not sum:
                column[j] /= summ              
        

    # transform G into markov matrix M
    M = csc_matrix(G,dtype=np.float)
    rsums = np.array(M.sum(1))[:,0]
    ri, ci = M.nonzero()
    M.data /= rsums[ri]

    # bool array of sink states
    sink = rsums==0

    # Compute pagerank r until we converge
    ro, r = np.zeros(n), np.ones(n)
    while np.sum(np.abs(r-ro)) > maxerr:
        ro = r.copy()
        # calculate each pagerank at a time
        for i in range(0,n):
            # inlinks of state i
            Ii = np.array(M[:,i].todense())[:,0]
            # account for sink states
            Si = sink / float(n)
            # account for teleportation to state i
            Ti = np.ones(n) / float(n)

            r[i] = ro.dot( Ii*s + Si*s + Ti*(1-s) )

    # return normalized pagerank
    return r/sum(r)



def import_idfs(filename):
    """
        Imports a dictionary of IDFs from a list of words sorted by inverse frequency.
    """
    ret = { }
    with open(filename) as f:
        i = 1
        for line in f.readlines():
            # Discard newline
            ret[line[:-1]] = i
            i += 1

    for key, value in ret.items():
        ret[key] = value / i

    return ret

idfs = import_idfs("../data/BingBodyDec13_Top100KWords.txt")

def tfs(words):
    """
        Returns a dictionary mapping words to their TF values.
    """
    ret = { }
    for word in words:
        if word in ret:
            ret[word] += 1
        else:
            ret[word] = 1

    return ret

def normalize(dd):
    """
        Normalizes all values of a dictionary.

        Modifies `dd`, returns nothing.
    """
    lo, hi = min(dd.values), max(dd.values)
    for key, value in dd.items():
        dd[key] = (value - lo) / (hi - lo)

def words(sentence):
    """
        Tokenizes a sentence.
        Returns a list of lowercase words containing no punctuation.
    """
    return "".join(e for e in sentence if e not in string.punctuation).lower().split()

def csim(tfidfs, a, b):
    """
        Cosine similarity of two lists of words `a` and `b`.
        
        Returns a float.
    """
    union = set()
    union.update(a)
    union.update(b)
    
    dot = 0
    alen = 0
    blen = 0
    for word in union:
        dot += tfidfs[word] * tfidfs[word] if (word in a and word in b) else 0
        alen += tfidfs[word] * tfidfs[word] if (word in a) else 0
        blen += tfidfs[word] * tfidfs[word] if (word in b) else 0

    norm = math.sqrt(alen) * math.sqrt(blen)

    return dot / norm if norm > 0 else 0

def centrality_scores(sentences):
    word_lists = [words(s) for s in sentences]
    freqs = tfs([i for l in word_lists for i in l]) # flatten word list
    tfidfs = { }

    for w in freqs.keys():
        tfidfs[w] = freqs[w] * (idfs[w] if w in idfs else 1)

    matrix = [[0 for i in range(len(word_lists))] for j in range(len(word_lists))]
    incidence = {}
    
   
    for i in range(0, len(sentences)):
        s1 = sentences[i]
        incidence[s1] = {}
        for j in range(0, len(sentences)):
            s2 = sentences[j]
            matrix[i][j] = csim(tfidfs, word_lists[i], word_lists[j])
            incidence[s1][s2] = csim(tfidfs, words(s1), words(s2))
           
    
    print(incidence)
    pagerank_scores = page_rank(matrix)

    scores = {}
    for i in range(0, len(sentences)):
        s = sentences[i]
        scores[s] = pagerank_scores[i]    
 
    return scores, incidence



def title_score(sentence, title):
    word_lists = [words(s) for s in [sentence, title]]
    tfidfs = { }
    freqs = tfs([i for l in word_lists for i in l]) # flatten word list
    
    for w in freqs.keys():
        tfidfs[w] = freqs[w] * (idfs[w] if w in idfs else 1)

    print(csim(tfidfs, words(sentence), words(title)))
    return csim(tfidfs, words(sentence), words(title))
   

def keyword_score(sentence, keywords):
    return sbfs(sentence, keywords) * dbfs(sentence, keywords)    


def sbfs(sentence, keywords):
    summ = 0.0
    for w in sentence.split():
        if w in keyword.keys():
             summ += keyword[w]
    
    return summ/len(sentence)
    
# keyword scores normalized between 0 and 1
def dbfs(sentence, keywords):
    keyword_count = 0
    summ = 0.0
    last_score = 0.0
    last_index = 0
    words = sentence.split()
    for i in range(0, len(words)):
        w = words[i]
        if w in keyword.keys():
            keyword_count += 1
            if not last_index:
                summ += (last_score*keywords[w])/pow(i - last_index)
            last_score = keywords[w]
            last_index = i

    if not keyword_count:
      return 0
    
    if keyword_count == 1:
      return epsilon

    return summ/(keyword_count - 1) 
    
def length_score(sentence):
    ideal = 20
    word_count = len(words(sentence))
    return abs(ideal - word_count)/ideal

def position_score(pos, sentence_count):
    normalize_pos = pos/sentence_count
    return pos_scores[math.floor(normalize_pos*10)]

def relevance_sentence_score(sentence, title, keywords, pos, sentence_count):
    #return 0.25*title_score(sentence, title) + 0.4*keyword_score(sentence, keywords) + \
     #   0.1*length_score(sentence) + 0.25*position_score(pos, sentence_count)
    return (0.25*title_score(sentence, title) +  \
        0.1*length_score(sentence) + 0.25*position_score(pos, sentence_count))/0.6

def relevance_scores(sentences, title, keywords):
    scores = {}
    for i in range(0, len(sentences)):
        s = sentences[i]
        scores[s] = relevance_sentence_score(s, title, keywords, i, len(sentences))
    return scores

def scale(cscores, rscores):
    maxr = max(list(rscores.values()))
    maxc = max(list(cscores.values()))
    for key in cscores.keys():
        cscores[key] *= (maxr/maxc)
    return cscores
    

def sentences_scores(sentences, title, keywords):
    rscores = relevance_scores(sentences, title, keywords)
    cscores, sim_matrix = centrality_scores(sentences)
    csores = scale(cscores, rscores)

    scores = {}
    for s in sentences:
        scores[s] = math.sqrt(rscores[s]*cscores[s])
    return scores, sim_matrix

# find score of k-th best sentence
# looks at [start, end)
def quick_select(scores, k):
    pivot = scores[0]
    left = []
    right = []
    for score in scores:
        if score < pivot:
            left.append(score)
        elif score > pivot:
            right.append(score)

    if k < len(left):
        return quick_select(left, k)
    elif k > len(left):
        return quick_select(right, k - len(left) - 1)
    else:
        return pivot

def select_best(scores, k):
    kth_best = quick_select(list(scores.values()), k)
    sentences = []
    for s in scores.keys():
        if scores[s] >= kth_best:
            sentences.append(s)

    return sentences
    
def maximal_similarity(s, summary_sentences, sim_matrix):
    maximal = 0.0
    for s2 in summary_sentences:
        maximal = max(maximal, sim_matrix[s][s2])

    return maximal

def maximal_marginal_relevance(scores, sorted_sentences, summary_sentences, sim_matrix):   
    lambd = 0.6
    max_score = 0.0
    max_sent = None
    for s in sorted_sentences:
        score = lambd*scores[s] - (1-lambd)*maximal_similarity(s, summary_sentences, sim_matrix)
        if score > max_score:
            max_score = score
            max_sent = s

    if max_sent:
        sorted_sentences.remove(max_sent)

    return max_sent
      
def summarize(sentences, title, keywords, summary_size):
    if summary_size >= len(sentences):    
        return sentences

    scores, sim_matrix = sentences_scores(sentences, title, keywords)
    sentences = select_best(scores, min(len(sentences), summary_size*2))
   
    sorted_sentences = sorted(sentences, key=lambda s: scores[s], reverse=True) 
    
    sum_sentences = []
    for i in range(0, summary_size):
        best_sent = maximal_marginal_relevance(scores, sorted_sentences, sum_sentences, sim_matrix)
        if best_sent:
            sum_sentences.append(best_sent)

    return sum_sentences

text = """Photo Advertisement Continue reading the main story

With a name like Leaf Greener (a literal translation of her Chinese name, Ye Zi) and clothing that ranges from a yolk-yellow Rosie Assoulin pantsuit at noon to a lacy Ronald van der Kemp evening gown after dark, surely you can make an impression during New York Fashion Week.

And that’s exactly what the Beijing-raised, Shanghai-based Ms. Greener had in mind.

Ms. Greener left Elle China last August after more than six years as senior fashion editor to strike out on her own as a stylist and fashion consultant. She kicked off New York Fashion Week last Wednesday by hobnobbing with some of fashion’s and beauty’s elite at an intimate cocktail party at the Fifth Avenue penthouse of Leonard Lauder. (She is currently featured in an Estée Lauder campaign in the Asia-Pacific region.)

By Friday, she had partied until 6 a.m. that morning, she confessed, but was doggedly doing the rounds of the young designers’ shows. “That’s what I care about most when I’m in New York, the new designers,” she said, looking inexplicably collected in her yellow suit despite the sweltering heat at Ms. Assoulin’s outdoor presentation. “They don’t call it Old York,” Ms. Greener added, laughing hard.

She whipped out her iPhone, housed in a case bought in Hong Kong that looked like a slice of cake, to take a video of the presentation for her Instagram account. She has nearly 100,000 followers on Instagram, even though it is banned in China, she pointed out, plus an even more devoted following on Chinese channels like WeChat and Weibo. “Everyone is on there or is moving to there,” Ms. Greener said, referring to WeChat. She publishes a mobile-only magazine on the platform.

Her fashion influence in China is such that brands like Chanel, Louis Vuitton and Lanvin have come calling (Ms. Greener consults or styles for them) and emerging brands vie for her attention. Ms. Assoulin, for one, greeted Ms. Greener enthusiastically, yelling out, “Leafie!”

She’s also featured in the Business of Fashion’s listing for people shaping the fashion industry.

“Fashion in China is changing,” Ms. Greener said between social media photos. “Before, it was all about logos and labels. It’s very similar to Russia in that way. You know, the communist country thing. But now people are interested in local young designers, and that’s an amazing thing. There are more contemporary fashion labels available now for the middle class.”

Compared to New Yorkers, she said, Chinese women are more willing to take fashion risks and perhaps to go for a full head-to-toe look, but they’re not as different as some in fashion may think.

“In Beijing, women will wear a lot of color and there’s more bling — it’s like L.A.,” Ms. Greener said. “In Shanghai, they like black or less obvious colors. They care about trends, and it’s more sophisticated like New York. Actually Beijing and Shanghai hate each other, so it really is like L.A. and New York. It’s good that I have a bit of both.” 

Cedar leaf oil is a sweet-smelling oil made from some types of cedar trees. Cedar leaf oil poisoning occurs when someone swallows this substance. Young children who smell the oil may try to drink it.

This is for information only and not for use in the treatment or management of an actual poison exposure. If you have an exposure, you should call your local emergency number (such as 911) or the National Poison Control Center at 1-800-222-1222. 

News about First Clover Leaf Financial Corporation, including commentary and archival articles published in The New York Times. 

WASHINGTON— THERE has never been a business lobby quite like Big Tobacco. For decades, its clout in Washington and state capitals was legendary, its prowess acknowledged by friend and foe.

Politicians crossed Big Tobacco at their peril. Most didn't try. Tobacco industry war chests poured cash into efforts to block new cigarette taxes and anti-smoking ordinances, to elect friends and crush enemies.

The Tobacco Institute, headquarters of the industry's effort to rebut the evidence that smoking makes people sick, was a Washington powerhouse. ''Dollar for dollar, they're probably the most effective lobby on Capitol Hill,'' Senator Edward M. Kennedy, the Massachusetts Democrat, said of it in 1979.

No more. State and local anti-smoking laws have swept the country in the face of Big Tobacco's strenuous objections. When President Clinton moved to restrict cigarette sales and advertising just 11 weeks before Election Day last year, he reckoned that he had more to gain from attacks on tobacco than he would lose in tobacco-growing states. Bob Dole, the Republican candidate, suffered politically when he suggested that tobacco might not be addictive and that the Government should not regulate it.

For anti-smoking crusaders, nothing has brought more joy than the waning influence of Big Tobacco.

Until now.

For suddenly last week, with the conclusion of an agreement by the industry to submit to regulation of tobacco as a drug, to curtail its advertising and to pay more than $360 billion in exchange for protection from lawsuits, Big Tobacco and its lifelong enemies now need each other.

A Skeptical Congress

And the deal cannot take effect without approval from a Congress that has already pronounced itself deeply skeptical. So, the anti-smoking forces that helped negotiate the new agreement have no hope of winning support for it unless the industry's lobbyists exert their influence.

Republicans like Representative Thomas J. Bliley Jr. of Virginia, long a friend of the industry, have scorned efforts by the Food and Drug Administration to regulate tobacco. The prospect that the industry will now urge him to support a vast expansion of the agency's powers boggles the mind. But such efforts will be necessary because Mr. Bliley is chairman of the House Commerce Committee, which has authority over the F.D.A.

Kathryn Kahler Vose, a spokeswoman for the Campaign for Tobacco-Free Kids, which took part in the negotiations, said: ''We have been at war with the tobacco companies. But we will urge Congress to support this package, and we anticipate that the tobacco companies will do so too. The nation will lose the many public health benefits of this agreement if Congress doesn't approve it. That would be really tragic.''

Tobacco companies described the settlement as ''a bitter pill,'' and in a joint statement, they said it called for new laws and regulations ''with which we do not necessarily agree'' -- a possible signal of trouble to come. But they promised to support it ''in order to achieve a resolution in the public interest.''

Although Big Tobacco has been on the defensive for years, it still has big resources that the anti-smoking forces lack, and need. Tobacco companies bankroll many of the super-lawyers and lobbyists in Washington. Its roster of advisers includes blue-ribbon firms like Covington & Burling, Arnold & Porter and Williams & Connolly.

How closely the state attorneys general, public health groups and cigarette makers will work together is unclear. But they share a common objective, translating their agreement into an enforceable Federal law.

For years to come, if the agreement survives, these strange bedfellows will depend on one another in ways they never have before. Together, they may become a new sort of lobby, prodding Congress to bless the agreement they forged.

The Lawyers Balk

Some people who hate cigarettes oppose the agreement simply on the ground that it does not go far enough to eradicate smoking. But more formidable opposition may come from plaintiffs' lawyers and their clients who want an unfettered opportunity to recover damages.

In a statement in January, the Association of Trial Lawyers of America said, ''Our court and jury system must not be denied the opportunity to hold the tobacco industry accountable in the best traditions of American justice.'' Howard F. Twiggs, president of the association, said then that ''Congress must not emasculate the very justice system that is only beginning to unearth the truth about tobacco.''

Several past presidents of the association took part in the negotiations on behalf of plaintiffs, but the group itself has indicated that it will oppose any provisions of a settlement that curtail the rights of future claimants.

The agreement seems to have already split the ranks of anti-smoking advocates. The American Cancer Society, the American Heart Association and the American Medical Association backed the settlement talks this month. But other anti-tobacco groups like the American Lung Association opposed them, fearing that the industry would gain more from a deal than consumers. All the groups are now evaluating the agreement. 

NYTimes.com no longer supports Internet Explorer 9 or earlier. Please upgrade your browser. 

IT has been called a tin can, a junker, a death trap and, in one particularly nasty case, ''an embarrassment to the neighborhood.'' The object of such scorn is our car, a 1990 Mitsubishi Mirage with 129,000 miles on her axles but, admittedly, none of the weathered grace one might expect of someone of her advancing age.

Mitzi, as my wife and I call her, aches from every CV joint. Her dull white frame is scarred and bruised. Her pale-blue interior is chafed and torn, with shards of plastic jutting out from the dashboard.

The plumbing is in no better shape. The car has had more valve replacements than Dick Cheney. More troubling, the scan button on the radio is busted, which makes finding a decent noncountry station akin to a 1950's ham radio operator trying to locate a late-night pal in Hässleholm.

My brother-in-law -- the proud owner of a sleek new Volvo sedan, a fully loaded Suburban and a 1969 G.T.O. he has been gingerly restoring since 1969 -- will demand, ''How can you drive that thing?'' The question is prompted more by concern than anything else, but he is a car guy. He sees only the mechanics.

I see something mysterious and, frankly, wonderful, and it happens like this. On weekend mornings my wife, Lee, and I grab Mitzi from her Upper West Side lot and begin driving north. We pass the Henry Hudson Bridge, then follow the narrow, winding Saw Mill River Parkway to the bucolic Taconic State Parkway, flooring the accelerator at the mere hint of open highway. Mitzi's bones creak under the pressure as the wind hisses through the slit of an open window. The speedometer hits 45.

Then, as Mitzi's four wheezing cylinders settle into a plaintive whine, one of us will start to speak. Somehow the subject matter is never about the weekend obligations that are coming due too fast or the household chores that are still undone. There is no mention of bills to be paid or overdue wedding gifts to be purchased. There is no talk even of jobs, of rough mornings, of long meetings, of missed opportunities.

As the highway loses itself in the landscape, the gray pavement melting into the greens and browns, we may find ourselves talking about . . . windows. Or one window, actually. It is a rectangular sweep of glass, with four beveled panels looking out onto the rocky Maine shoreline. I begin to describe my dream house, the slightly drafty, cedar-shingled Victorian, with the wide turrets and the backyard rolling into the water.

Lee listens intently and then says, ''Car talk?''

''Car talk,'' I respond.

And the ritual is sealed. For some reason, with those two words said, it is easier to talk. I go on describing the dream house and my visions of teaching in tiny New England college towns and late-night dinners with friends around a big wooden table. At some point -- minutes, sometimes an hour later -- the topic winds its way to completion. Lee will then remark on the color of the sky, or relate a long, strange dream she had the week before. It may conjure up the subject of her next screenplay, or she will tell me, from beginning to end, the story of a novel she's reading.

''Car talk?'' I ask.

''Car talk,'' she responds.

In truth, though, this talk is monologue, not conversation. There is something about the whirr of the engine, the trash strewn on the floor mats, the smell of old coffee that makes good listeners of both of us. Maybe that, more than the ability to share secrets and dreams, is what is so mysterious about the sessions.

We have often tried to duplicate the phenomenon at home, or even on short drives to Queens to visit relatives. But it rarely works. At home, the phone rings or dinner calls; on the drive to Queens, the traffic is aggressive and distracting. Our conversations are often great but short, focusing on the prosaic.

Mitzi wheezes and whines and coughs as Volvos weave past her on the Long Island Expressway. The exhaust hangs over La Guardia, and it is clear that the car isn't in the mood for talk. At times like these, she does feel as old as she looks.

It is also at times like these that I realize that, some day, we will have to buy a new car. One that does zero to 60 in seconds. One with fine leather trim, a 50-CD changer, and new car smell. One my brother-in-law will be proud of.

What a sad day that will be.

Drawing (Lars Leetaru) 

Advertisement Continue reading the main story

EVERY spring, some 30,000 oncologists, medical researchers and marketers gather in an American city to showcase the latest advances in cancer treatment.









But at the annual meeting of the American Society of Clinical Oncology last month, much of the buzz surrounded a study that was anything but a breakthrough. To a packed and whisper-quiet room at the McCormick Place convention center in Chicago, Mark R. Gilbert, a professor of neuro-oncology at the University of Texas M. D. Anderson Cancer Center in Houston, presented the results of a clinical trial testing the drug Avastin in patients newly diagnosed with glioblastoma multiforme, an aggressive brain cancer. In two earlier, smaller studies of patients with recurrent brain cancers, tumors shrank and the disease seemed to stall for several months when patients were given the drug, an antibody that targets the blood supply of these fast-growing masses of cancer cells.

But to the surprise of many, Dr. Gilbert’s study found no difference in survival between those who were given Avastin and those who were given a placebo.

Photo

Disappointing though its outcome was, the study represented a victory for science over guesswork, of hard data over hunches. As far as clinical trials went, Dr. Gilbert’s study was the gold standard. The earlier studies had each been “single-arm,” in the lingo of clinical trials, meaning there had been no comparison group. In Dr. Gilbert’s study, more than 600 brain cancer patients were randomly assigned to two evenly balanced groups: an intervention arm (those who got Avastin along with a standard treatment) and a control arm (those who got the latter and a placebo). What’s more, the study was “double-blind” — neither the patients nor the doctors knew who was in which group until after the results had been assessed.

The centerpiece of the country’s drug-testing system — the randomized, controlled trial — had worked.

Except in one respect: doctors had no more clarity after the trial about how to treat brain cancer patients than they had before. Some patients did do better on the drug, and indeed, doctors and patients insist that some who take Avastin significantly beat the average. But the trial was unable to discover these “responders” along the way, much less examine what might have accounted for the difference. (Dr. Gilbert is working to figure that out now.)

Indeed, even after some 400 completed clinical trials in various cancers, it’s not clear why Avastin works (or doesn’t work) in any single patient. “Despite looking at hundreds of potential predictive biomarkers, we do not currently have a way to predict who is most likely to respond to Avastin and who is not,” says a spokesperson for Genentech, a division of the Swiss pharmaceutical giant Roche, which makes the drug.

That we could be this uncertain about any medicine with $6 billion in annual global sales — and after 16 years of human trials involving tens of thousands of patients — is remarkable in itself. And yet this is the norm, not the exception. We are just as confused about a host of other long-tested therapies: neuroprotective drugs for stroke, erythropoiesis-stimulating agents for anemia, the antiviral drug Tamiflu — and, as recent headlines have shown, rosiglitazone (Avandia) for diabetes, a controversy that has now embroiled a related class of molecules. Which brings us to perhaps a more fundamental question, one that few people really want to ask: do clinical trials even work? Or are the diseases of individuals so particular that testing experimental medicines in broad groups is doomed to create more frustration than knowledge?

Advertisement Continue reading the main story

Researchers are coming to understand just how individualized human physiology and human pathology really are. On a genetic level, the tumors in one person with pancreatic cancer almost surely won’t be identical to those of any other. Even in a more widespread condition like high cholesterol, the variability between individuals can be great, meaning that any two patients may have starkly different reactions to a drug.

That’s one reason that, despite the rigorous monitoring of clinical trials, 16 novel medicines were withdrawn from the market from 2000 through 2010, a figure equal to 6 percent of the total approved during the period. The pharmacogenomics of each of us — the way our genes influence our response to drugs — is unique.

HUMAN drug trials are typically divided into three phases. In the first, researchers evaluate the safety of a new experimental compound in a small number of people, determining the best way to deliver it and the optimal dosage. In Phase 2, investigators give the drug to a larger number of patients, continuing to monitor its safety as they assess whether the agent works.

“Works” in this stage is broadly defined. Seeing that the drug has any positive effect at all — say, that it decreases the level of a blood marker associated with a disease — is often enough to move a drug to Phase 3. Even so, most experimental drugs fail before they get to Phase 3.

The few that make it to Phase 3 are then tested for safety and efficacy in hundreds or thousands of patients. This time, the outcomes for those taking the new drug are typically compared head-to-head with outcomes for those getting a placebo or the standard-of-care therapy. Generally, the Food and Drug Administration requires that two “adequate and well-controlled” trials confirm that a drug is safe and effective before it approves it for sale, though the bar can be lower in the case of medicines aimed at life-threatening conditions.

Rigorous statistical tests are done to make sure that the drug’s demonstrated benefit is genuine, not the result of chance. But chance turns out to be a hard thing to rule out. When the measured effects are small — as they are in the vast majority of clinical trials — mere chance is often the difference between whether a drug is deemed to work or not, says John P. A. Ioannidis, a professor of medicine at Stanford.

In a famous 2005 paper published in The Journal of the American Medical Association, Dr. Ioannidis, an authority on statistical analysis, examined nearly four dozen high-profile trials that found a specific medical intervention to be effective. Of the 26 randomized, controlled studies that were followed up by larger trials (examining the same therapy in a bigger pool of patients), the initial finding was wholly contradicted in three cases (12 percent). And in another 6 cases (23 percent), the later trials found the benefit to be less than half of what was first reported.

Advertisement Continue reading the main story

It wasn’t the therapy that changed in each case, but rather the sample size. And Dr. Ioannidis believes that if more rigorous, follow-up studies were actually done, the refutation rate would be far higher.

Advertisement Continue reading the main story

Donald A. Berry, a professor of biostatistics at M. D. Anderson, agrees. He, too, can rattle off dozens of examples of this evaporation effect and has made a sport, he says, of predicting it. The failures of the last 20 or so Phase 3 trials testing drugs for Alzheimer’s disease, he says, could have been predicted based on the lackluster results from Phase 2. Still, the payoff for a successful Phase 3 trial can be so enormous that drug makers will often roll the dice — not on the prospect that the therapy will suddenly work, but on the chance that a trial will suggest that it does.

Photo

At a round-table discussion a few years ago, focused on the high failure rate for Alzheimer’s drugs, Dr. Berry was amazed to hear one drug company researcher admit to such thinking out loud. The researcher said that when he and his team designed the Phase 3 trial, he thought the drug would probably fail. But if they could get an approval for a drug for Alzheimer’s disease, it would be “a huge success.”

“What he was saying,” marvels Dr. Berry, “was, ‘We’re playing the lottery.’ ”

The fact that the pharmaceutical companies sponsor and run the bulk of investigative drug trials brings what Dr. Ioannidis calls a “constellation of biases” to the process. Too often, he says, trials are against “a straw-man comparator” like a placebo rather than a competing drug. So the studies don’t really help us understand which treatments for a disease work best.

But a more fundamental challenge has to do with the nature of clinical trials themselves. “When you do any kind of trial, you’re really trying to answer a question about truth in the universe,” says Hal Barron, the chief medical officer and head of global development at Roche and Genentech. “And, of course, we can’t know that. So we try to design an experiment on a subpopulation of the world that we think is generalizable to the overall universe” — that is, to the patients who will use the drug.

That’s a very hard thing to pull off. The rules that govern study enrollment end up creating trial populations that invariably are much younger, have fewer health complications and have been exposed to far less medical treatment than those who are likely to use the drug.

Roughly 53 percent of new cancer diagnoses, for example, are in people 65 or older, but this age group accounts for just 33 percent of participants in cancer drug trials.

Even if clinical researchers could match the demographics of study populations to those of the likely users of these medicines, no group of trial volunteers could ever match the extraordinary biological diversity of the drugs’ eventual consumers.

Drug makers are well aware of the challenge. “Listen, it’s not lost on anybody that about 95 percent of drugs that enter clinical testing fail to ever get approved,” says Dr. Barron. “It’s not hard to imagine that at least some of those might have failed because they work very, very well in a small group. We can’t continue to have failures due to a lack of appreciation of this heterogeneity in diseases.”

Advertisement Continue reading the main story

Advertisement Continue reading the main story

So what’s the solution? For subtypes of disease that are already known, it may be feasible to design small clinical trials and enroll only those who have the appropriate genetic or molecular signature. That’s what Genentech did in developing the breast cancer drug Herceptin, which homes in on tumor cells that have an abundance of a protein called HER2.

And that’s the strategy the company says it’s pursuing now. Sixty percent of the new drugs in the works at Genentech/Roche are being developed with a companion diagnostic test to identify the patients who are most likely to benefit.

But given the dismal success rate for drug development, this piecemeal approach is bound to be slow and arduous. Rather than try to fit patients, a handful at a time, into the decades-old clinical-trials framework, we’d be far better off changing the trials themselves.

In fact, a breast cancer trial called I-SPY 2, already under way, may be a good model to follow. The aim of the trial, sponsored by the Biomarkers Consortium, a partnership that includes the Foundation for the National Institutes of Health, the F.D.A., and others, is to figure out whether neoadjuvant therapy for breast cancer — administering drugs before a tumor is surgically removed — reduces recurrence of the disease, and if so, which drugs work best.

As with the Herceptin model, patients are being matched with experimental medicines that are designed to target a particular molecular subtype of breast cancer. But unlike in other trials, I-SPY 2 investigators, including Dr. Berry, are testing up to a dozen drugs from multiple companies, phasing out those that don’t appear to be working and subbing in others, without stopping the study.

Part of the novelty lies in a statistical technique called Bayesian analysis that lets doctors quickly glean information about which therapies are working best. There’s no certainty in the assessment, but doctors get to learn during the process and then incorporate that knowledge into the ongoing trial.

Mark Gilbert, for his part, would even settle for something simpler in his next glioblastoma study. His definition of a successful clinical trial? “At the end of the day,” he says, “regardless of the result, you’ve learned something.” 

Thank you for visiting The New York Times archive.

New York Times subscribers* enjoy full access to TimesMachine—view 129 years of New York Times journalism, as it originally appeared. 99¢ for your first 4 weeks.

Or, purchase this article individually for $3.95 and download a high-resolution PDF. 

Thank you for visiting The New York Times archive.

New York Times subscribers* enjoy full access to TimesMachine—view 129 years of New York Times journalism, as it originally appeared. 99¢ for your first 4 weeks.

Or, purchase this article individually for $3.95 and download a high-resolution PDF. 

Are leaf blowers a welcome labor-saving convenience or a noisy nuisance? Should their use be limited?

Not a Fan of Blowers

I hate, hate, hate leaf blowers. Here in the suburbs the decibels they produce is a serious threat to health and mental sanity. They should be limited to parks, golf courses and large estates and taxed as noise polluters.

MILTON JAFFE

Fair Lawn

Just Another Gadget

I believe a leaf blower is just another gadget. Yes, it makes noise but as long as it is not used on a Saturday morning before 8 A.M. I am fine with it.

DEE HICKMAN

Hillsborough

Remember the Rake?

Leaf blowing is a lazy approach to an easy job. Creating noise as well as air pollution, leaf blowers do the same job as a rake. The rake: a primitive tool, long forgotten. In a society where pollution is big and weight-watching even bigger, the rake is a pollution-free and calorie-burning way to clear the yard.

PETE SANKOWICH

Midland Park

Popular With the Neighbors

The subject of leaf blowers touches a very sore spot. We live in a lovely section of Toms River. I guess six of our neighbors own leaf blowers, and the five others employ professional gardeners. It's a tossup as to which is worse.

I wrote to the mayor, only to find that leaf blowers are permitted seven days a week until 7 P.M. The owners love to practice with them, mostly between 6 and 7 P.M., when we are driven off our back deck by the unbearable racket. On, off; off, on, is the worst part.

Yes, there should be a law. The leaf blowers are much worse than lawn mowers. Five o'clock should be the deadline.

The sad part of the whole thing is that leaf blowers often just blow the dirt and leaves onto the street, to later blow onto the neighbor's driveway or lawn.

BOB LONG

Toms River

There Are Worse Noises

Leaf blowers may be a noisy nuisance but in my opinion the sound of a metal rake grating against concrete is even worse.

KRISTEN TORRES

Midland Park 

Opinion » Should Beach Privatization Be Allowed? Room for Debate asks whether shorefront homeowners should have to open their land to all comers.

Opinion » Op-Ed: Elite, Separate, Unequal New York City’s top public schools must become more diverse. 

Opinion » Should Beach Privatization Be Allowed? Room for Debate asks whether shorefront homeowners should have to open their land to all comers.

Opinion » Op-Ed: Elite, Separate, Unequal New York City’s top public schools must become more diverse. 

Opinion » Should Beach Privatization Be Allowed? Room for Debate asks whether shorefront homeowners should have to open their land to all comers.

Opinion » Op-Ed: Elite, Separate, Unequal New York City’s top public schools must become more diverse. 

Opinion » Should Beach Privatization Be Allowed? Room for Debate asks whether shorefront homeowners should have to open their land to all comers.

Opinion » Op-Ed: Elite, Separate, Unequal New York City’s top public schools must become more diverse. 

Opinion » Should Beach Privatization Be Allowed? Room for Debate asks whether shorefront homeowners should have to open their land to all comers.

Opinion » Op-Ed: Elite, Separate, Unequal New York City’s top public schools must become more diverse. 

Opinion » Should Beach Privatization Be Allowed? Room for Debate asks whether shorefront homeowners should have to open their land to all comers.

Opinion » Op-Ed: Elite, Separate, Unequal New York City’s top public schools must become more diverse. 

Thank you for visiting The New York Times archive.

New York Times subscribers* enjoy full access to TimesMachine—view 129 years of New York Times journalism, as it originally appeared. 99¢ for your first 4 weeks.

Or, purchase this article individually for $3.95 and download a high-resolution PDF. 

CHICAGO, July 9.--Dr. Orlando P. Scott, one of Chicago's best known surgeons, who as a Captain in the Medical Corps of the American Army operated on liquid fire cases on the French battlefields, today performed one of the most... 

SPRINGFIELD, Ill., April 20. -- In the Wabash Railroad Company's hospital here is a case of bona fide bone grafting, the human limb being supported and strengthened by bone taken from a live chicken. John Dougherty, a section hand, while working in the Chicago yards June 14, 1890, received a slight injury to his left shinbone by scraping the skin off while placing a piece of timber on the ground. 

Thank you for visiting The New York Times archive.

New York Times subscribers* enjoy full access to TimesMachine—view 129 years of New York Times journalism, as it originally appeared. 99¢ for your first 4 weeks.

Or, purchase this article individually for $3.95 and download a high-resolution PDF. 

As a result of investigations concerning the extent of the kaolin deposits in Puolanka, Finland, that have been made this Summer, it has been found that there are actually at least 10,000 tons of it there and an estimated probability of ... 

NEWARK, May 14. -- An injunction was granted by Vice Chancellor Emery here to-day, restraining the stocknolders of the International Kaolin Company from leasing or discharging any of the property of the concern, a receiver for which was appointed recently. The bill granted by the Vice Chancellor is returnable May 27. 

Thank you for visiting The New York Times archive.

New York Times subscribers* enjoy full access to TimesMachine—view 129 years of New York Times journalism, as it originally appeared. 99¢ for your first 4 weeks.

Or, purchase this article individually for $3.95 and download a high-resolution PDF. 

Opinion » Should Beach Privatization Be Allowed? Room for Debate asks whether shorefront homeowners should have to open their land to all comers.

Opinion » Op-Ed: Elite, Separate, Unequal New York City’s top public schools must become more diverse. 

IN an unusual attempt at regional land planning, four major landowners in this mushroom-growing area have joined in an informal master plan for 2,000 acres.

More famous for the pungent odor of mushroom compost than for its rolling countryside, the land in southern Chester County bordering Delaware has been spared heavy development, largely because it has been controlled by a few families, including two mushroom growers.

But now that the largest landowner in the area is trying to develop his family's holdings, the other big owners have agreed to draw up a comprehensive plan for developing both sides of Route 41. Led by Charles Raskob Robinson of Manhattan, whose family owns 450 acres, the four have proposed an 18-hole golf course, a retirement community, a hotel conference center, a town center, luxury homes and open space.

Kaolin Commons, as the project has been named, encompasses all the smaller landowners and all existing development. The drafters have no real authority over the others, nor will they unite as a corporate entity. The plan is essentially a gentlemen's agreement. The owners will develop independently and retain their properties.

All the development will have to go through a complete land review by both the township and county.

Work has begun on two housing communities on the northern and southern ends of the 2,000-acre parcel. One community, known as Hartefeld, is being developed by Mr. Robinson.

The other, called Somerset Lake, is a project of Bellevue Holding Company of Wilmington, Del.

Mr. Robinson, whose grandfather was the financierJohn Jacob Raskob, said the need for a comprehensive plan became apparent five years ago when he put the family's estate on the market. Buyers loved the site but were concerned about future development on adjoining properties, Mr. Robinson said. At that point he decided to develop the parcel himself.

The priority for the Robinson land in 1991 is the golf course, which is intended to be a deluxe public course. The family's sprawling 10-bedroom home will be converted into a clubhouse. The course will be named Hartefeld National.

Mr. Robinson is also working on developing a 300-unit retirement community within walking distance of both the town center and the golf course.

Preliminary plans for the town center, to be developed on land owned by Bellevue Holding Company and the Pia mushroom-farming family, will have a hotel and a village shopping area. The fourth big owner is the Ciarrochi family.

Photo: Clubhouse for Kaolin Commons, 2,000-acre project with golf course and residences in Kaolin, Pa. (Wright Associates) 

IN an unusual attempt at regional land planning, four major landowners in this mushroom-growing area have joined in an informal master plan for 2,000 acres.

More famous for the pungent odor of mushroom compost than for its rolling countryside, the land in southern Chester County bordering Delaware has been spared heavy development, largely because it has been controlled by a few families, including two mushroom growers.

But now that the largest landowner in the area is trying to develop his family's holdings, the other big owners have agreed to draw up a comprehensive plan for developing both sides of Route 41. Led by Charles Raskob Robinson of Manhattan, whose family owns 450 acres, the four have proposed an 18-hole golf course, a retirement community, a hotel conference center, a town center, luxury homes and open space.

Kaolin Commons, as the project has been named, encompasses all the smaller landowners and all existing development. The drafters have no real authority over the others, nor will they unite as a corporate entity. The plan is essentially a gentlemen's agreement. The owners will develop independently and retain their properties.

All the development will have to go through a complete land review by both the township and county.

Work has begun on two housing communities on the northern and southern ends of the 2,000-acre parcel. One community, known as Hartefeld, is being developed by Mr. Robinson. The other, called Somerset Lake, is a project of Bellevue Holding Company of Wilmington, Del.

Mr. Robinson, whose grandfather was the financierJohn Jacob Raskob, said the need for a comprehensive plan became apparent five years ago when he put the family's estate on the market. Buyers loved the site but were concerned about future development on adjoining properties, Mr. Robinson said. At that point he decided to develop the parcel himself.

The priority for the Robinson land in 1991 is the golf course, which is intended to be a deluxe public course. The family's sprawling 10-bedroom home will be converted into a clubhouse. The course will be named Hartefeld National.

Mr. Robinson is also working on developing a 300-unit retirement community within walking distance of both the town center and the golf course.

Preliminary plans for the town center, to be developed on land owned by Bellevue Holding Company and the Pia mushroom-farming family, will have a hotel and a village shopping area. The fourth big owner is the Ciarrochi family.

Photo: Clubhouse for Kaolin Commons, 2,000-acre project with golf course and residences in Kaolin, Pa. (Wright Associates) 

Thank you for visiting The New York Times archive.

New York Times subscribers* enjoy full access to TimesMachine—view 129 years of New York Times journalism, as it originally appeared. 99¢ for your first 4 weeks.

Or, purchase this article individually for $3.95 and download a high-resolution PDF. 

A mortgage for $500,000, made by the Delmont Kaolin Deposit Company of Sea Cliff and New-York in favor of the Central Trust Company of New-York, was filed in the County Clerk's office, at Jamaica, L.I. yesterday. Later in the day Under Sheriff Sharkey of Queens County seized the plant and property of the Delmont Kaolin Deposit Company, at Sea Cliff, upon executions in favor of J.H. Grosjean for $3,564 and Johnson B. Creighton for $11,600. 

KAOLIN, Pa.— HAVING grown up in mushroom country, Charles Raskob Robinson remembers days when the stench wafting from nearby composting operations would take his breath away.

''Chicken manure has a real kick,'' Mr. Robinson said, referring to the fermentation of a mixture of chicken and horse manure, corncobs, hay and straw that create the prime growing medium for mushrooms.

The odors were little more than an occasional olfactory nuisance until Mr. Robinson, the grandson of John Jacob Raskob -- the financier who built the Empire State Building -- decided to develop his family's 460-acre estate in southeastern Pennsylvania in the mid-1980's.

''It basically lessened the value'' of most of his land, said Mr. Robinson, a Manhattan artist.

Fortunately for him, the mushroom growers near his Colonial Farms estate agreed, recognizing that community opposition was only going to increase as new home developments edged closer to the farms.

The four major landowners nearby -- Mr. Robinson, two prominent mushroom farmers and a developer -- met to create a master plan that would allow for orderly development of their lands along Route 41 south of Kennett Square. Their combined properties, roughly 30 miles southwest of Philadelphia, total about 2,000 acres. And they were unanimous in their opinion that something had to be done about the composting operation.

The result was construction of the country's first indoor composting operation. Kaolin Mushroom Farms Inc. of Kennett Square, Pa., the largest mushroom operation in Chester County and among the biggest in the country, is finishing work on a $3 million building that should control 90 percent of the odors.

When the building is completed in November, Kaolin Mushroom will be one of a handful of mushroom growers in the world to be entirely indoors. Not only is the operation expected to be more efficient, cutting the compost curing time by 65 percent, but it also promises to free more than 200 acres of prime property for commercial development.

The new building will allow Kaolin Mushroom to reduce the amount of land needed for the mushroom growing medium, or substrate, to 2 acres from 14 acres. Currently, huge outdoor mounds of organic matter are watered and blended for about 21 days until the microbes have had a chance to break down the ingredients. During the fermentation process, temperatures reach up to 175 degrees Fahrenheit.

In general, the compost smell should be mild. It is only when the piles become starved of oxygen that noxious anaerobic activity begins. This should be held under control in the new building.

Michael L. Pia, president of the privately held Kaolin Mushroom Farms, said he was already getting interest from real estate developers for the 170 acres owned by his family. Mr. Robinson is also a partner in another 40 acres of contiguous land.

THE master plan drawn up by the four landowners calls for a town center that could accommodate up to 700,000 square feet of retail and office development. The property owners have also agreed to a town hall, post office, church and retirement community, Mr. Robinson said. The development concept has received the blessing of New Garden Township officials.

In addition to the Pias and Mr. Robinson, the two other major landowners in the area are the Ciarrochis, mushroom growers who own Modern Mushroom Farms Inc., and Bellevue Holding Company, a real estate development firm based in Wilmington, Del.

All this has led to intense interest among mushroom growers across the country. If the indoor composting operation is successful, it could be a solution to the mounting conflict between mushroom farmers and residents of new bedroom communities.

''Urban encroachment is one of the biggest challenges facing the industry today,'' said Laura Phelps, president of the American Mushroom Institute in Washington. ''Complaints about odors just make it more difficult to do business.''

While mushrooms are grown throughout the country, a majority of the nation's 165 growers of Agaricus bisporus -- the common button mushroom -- are in Pennsylvania. But whether as a result of development or consolidation, the number of Pennsylvania mushroom farmers has declined by 80 percent since 1980, according to Paul J. Wuest, a plant pathologist at Pennsylvania State University.

Some farms go the way of the bulldozer for new home developments, and other farms are sold to mushroom growers.

''You have these beautiful farms of 100 to 200 acres that have been in the family for a couple generations and they're selling off,'' said John B. Swayne 3d, president of J. B. Swayne Spawn Company in Kennett Square, whose grandfather started the nation's mushroom business. ''You're torn because maybe that's going to be their savings to enjoy retirement.''

The consolidation of smaller mushroom operations with larger growers has only worsened the odor problem, because the composting operations, while fewer, are much larger. Kaolin Mushroom, for example, uses about 20 million pounds of poultry manure a year to make compost. 

Precious Chalk

Q. What is kaolin and where does it come from? Is the kaolin in diarrhea medication the same as the clay in china?

A. Kaolin, also called China clay, is a chalky rock composed chiefly of kaolinate, together with quartz and mica. It is formed by the weathering of aluminum-rich silicate rocks, especially feldspar. Over the ages, the crystals wash into large sedimentary deposits. The formula for pure kaolinate is Al2 Si2 O5 (OH)4 , Van Nostrand's Scientific Encyclopedia says.

Purified kaolin in a suspension with pectin from apples has long been use to fight diarrhea. It is a gastrointestinal adsorbent, believed to attract and hold microbes that may be causing the diarrhea. The action of pectin is not known.

Kaolin is said to derive its name from an area of China with extensive deposits of the mineral. It is found in many other places famous for china, like Meissen, Germany, Limoges, France, and parts of England.

There are also kaolin deposits in the United States, including a great chalk mark across the state of Georgia. The China Clay Producers Association says the Georgia deposit dates from 50 million to 100 million years ago, during the Cretaceous and Tertiary periods, when the Atlantic Ocean covered much of Georgia south of a line drawn from Columbus to Augusta.

Above this line, known as the Fall Line, crystalline rocks from the Piedmont Plateau began to break down, and streams carried the tiny crystals seaward. The deposits were later covered with heavy layers of earth. C. CLAIBORNE RAY

Drawing (Victoria Roberts) 
"""

lines = [t.strip() for t in re.split("(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text.replace("\n", " "))]

print(summarize(lines, "Computers", [], 2))
