db.atelier.aggregate(
[{$unwind: {
 path: '$reservations'
}}, {$project: {
 _id: 0,
 date: 1,
 reservations: 1
}}, {$sort: {
 'reservations.id': 1
}}, {$out: 'reservations'}]
).pretty()