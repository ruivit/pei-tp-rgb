db.atelier.aggregate(
[{$sort: {
    active_reservations: -1
   }}, {$project: {
    _id: 0,
    date: 1,
    OccupacionPercentage: {
     $concat: [
      {
       $toString: {
        $multiply: [
         {
          $divide: [
           '$active_reservations',
           50
          ]
         },
         100
        ]
       }
      },
      '%'
     ]
    }
   }}]
   ).pretty()