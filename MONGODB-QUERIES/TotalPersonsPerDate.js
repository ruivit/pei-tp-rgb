[{$unwind: {
    path: '$reservations'
   }}, {$group: {
    _id: '$date',
    TotalPersonsPerDate: {
     $sum: '$reservations.family.numberElements'
    }
   }}, {$sort: {
    TotalPersonsPerDate: -1
   }}, {$addFields: {
    date: '$_id'
   }}, {$project: {
    _id: 0,
    date: 1,
    TotalPersonsPerDate: 1
   }}]