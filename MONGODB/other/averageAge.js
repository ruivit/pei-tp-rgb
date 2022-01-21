db.atelier.aggregate(
[{$unwind: {
 path: '$reservations'
}}, {$match: {
 'reservations.state': 'Active'
}}, {$project: {
 average: {
  $avg: '$reservations.family.familyElement.age_when_visiting'
 }
}}, {$group: {
 _id: null,
 Average_Age: {
  $avg: '$average'
 }
}}]
).pretty()
