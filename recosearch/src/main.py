from modules.Processor import Processor

pr = Processor()

profile = pr.create_group_information(word_count=5)

dataset = pr.create_group_dataset(profile)

# similarities = pr.get_profile_similarities(profile, dataset)

profile.to_csv("profile.csv", index=False)
dataset.to_csv("query2.csv", index=False)
