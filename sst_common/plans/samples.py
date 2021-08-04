from .motors import sample_holder
import csv

filename = "../../examples/sample_load.csv"
def read_sample_csv(filename):
    with open(filename, 'r') as f:
        sampleReader = csv.reader(f)
        samplelist = [row for row in sampleReader]
        #rownames = [n for n in samplelist[0] if n != ""]
        rownames = ["sample_id", "sample_name", "side", "x1", "y1", "x2", "y2", "t", "tags"]
        samples = {}
        for sample in samplelist[1:]:
            sample_id = sample[0]
            sample_dict = {key: sample[rownames.index(key)] for key in rownames[1:-1]}
            sample_tags = sample[rownames.index("tags"):]
            sample_dict['tags'] = [t for t in sample_tags if t != ""]
            samples[sample_id] = sample_dict
    return samples

def load_samples_into_holder(filename, holder):
    holder._reset()
    samples = read_sample_csv(filename)
    for sample_id, s in samples.items():
        position = (s['x1'], s['y1'], s['x2'], s['y2'])
        name = s['sample_name']
        side = s['side']
        thickness = s['t']
        holder.add_sample(sample_id, name, position, side, thickness)

def load_samples(filename):
    load_samples_into_holder(sample_holder)
    
