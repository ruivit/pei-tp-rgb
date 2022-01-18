[{$unwind: {
    path: '$reservations'
   }}, {$match: {
    'reservations.state': 'Canceled'
   }}, {$group: {
    _id: '$date',
    NumberOfCanceled: {
     $sum: 1
    }
   }}, {$sort: {
    NumberOfCanceled: -1
   }}, {$addFields: {
    date: '$_id'
   }}, {$project: {
    _id: 0,
    date: 1,
    NumberOfCanceled: 1,
    OccupacionPercentage: {
     $concat: [
      {
       $toString: {
        $multiply: [
         {
          $divide: [
           '$NumberOfCanceled',
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