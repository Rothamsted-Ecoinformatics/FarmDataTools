import json
import datetime
import farmService

farm = farmService.myFarm()

taxonomyId = 387 # edit this
newTaxonomyId = 388 # edit this
taxonomyRecord = farm.term.get(taxonomyId)
newTaxonomyRecord = farm.term.get(newTaxonomyId)
print(json.dumps(newTaxonomyRecord, indent=4, sort_keys=True))

inputs = farm.log.get(filters={'type': 'farm_input'})['list']

for input in inputs:
    materials = input['material']
    newMaterials = []
    #print(input)
    for m in [y for y in materials if y['uri'] == 'https://rothamstedfarm.farmos.net/taxonomy_term/'+str(taxonomyId)]:
        print(json.dumps(input, indent=4, sort_keys=True))
        for material in materials:
            if material['uri'] == 'https://rothamstedfarm.farmos.net/taxonomy_term/'+str(taxonomyId):
                newMaterials.append({"id":newTaxonomyId,"name":newTaxonomyRecord["name"],"resource":"taxonomy_term","uri":'https://rothamstedfarm.farmos.net/taxonomy_term/'+str(newTaxonomyId)})
            else:
                newMaterials.append(material)    

        # create an updated version of the record (we're going to swap them out), removing empty keys
        newInput = {}
        for key, value in input.items():            
            if value:
                print(key + ": " + str(value))
                newInput[key] = value

        newInput["material"] = newMaterials
        del newInput["movement"] # this is null and easiest to just remove
        print(json.dumps(newInput, indent=4, sort_keys=True))

        #delete the original version
        farm.log.delete(input["id"])

        #upload the replacement version - ##Simply copying this won't work - need to remove / replace nulls and remove the ID and URL values.
        farm.log.send(newInput)

# delete the taxonomy term
farm.term.delete(taxonomyId)