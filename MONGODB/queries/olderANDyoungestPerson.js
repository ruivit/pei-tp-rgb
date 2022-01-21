db.atelier.aggregate(
[{$unwind: {
 path: '$reservations'
}}, {$match: {
 'reservations.state': 'Active'
}}, {$unwind: {
 path: '$reservations.family.familyElement'
}}, {$sort: {
 'reservations.family.familyElement.age_when_visiting': 1
}}, {$project: {
 'reservations.family.familyElement.name': 1,
 'reservations.family.familyElement.age_when_visiting': 1
}}, {$limit: 1}]
).pretty()

db.atelier.aggregate(
[{$unwind: {
 path: '$reservations'
}}, {$match: {
 'reservations.state': 'Active'
}}, {$unwind: {
 path: '$reservations.family.familyElement'
}}, {$sort: {
 'reservations.family.familyElement.age_when_visiting': 1
}}, {$project: {
 'reservations.family.familyElement.name': 1,
 'reservations.family.familyElement.age_when_visiting': 1
}}, {$limit: 1}]
).pretty()