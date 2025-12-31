from datalog import Datalog


EXAMPLE_DATALOG = """{
    "subjects": "Patient(P), Prescriber(D).",
    "objects": "Drug(DR).",
    "relationships": "has_allergy(P, DR) :- Patient(P), Drug(DR).",
    "actions": "can_prescribe(D, P, DR) :- Prescriber(D), Patient(P), Drug(DR), not has_allergy(P, DR)."
}"""

datalog = Datalog(EXAMPLE_DATALOG)
datalog_specs = datalog.specifications()
print("Datalog Specifications:")
for key, value in datalog_specs.items():
    print(f"{key}: {value}")
