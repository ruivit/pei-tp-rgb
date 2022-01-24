db.atelier.aggregate(
[{$unwind: {
    path: '$reservations'
   }}, {$group: {
    _id: '$reservations.family.origin'
   }}, {$replaceRoot: {
    newRoot: '$_id'
   }}, {$project: {
    _id: 0,
    countryName: 1,
    cityName: 1
   }}, {$out: 'countries'}]
).pretty()

db.atelier.aggregate(
[{$unwind: {
    path: '$reservations'
   }}, {$group: {
    _id: '$reservations.family.origin'
   }}, {$replaceRoot: {
    newRoot: '$_id'
   }}, {$group: {
    _id: '$countryName',
    Cities: {
     $push: '$cityName'
    }
   }}, {$out: 'countriesANDcities'}]
).pretty()