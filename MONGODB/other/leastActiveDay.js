db.atelier.aggregate(
[{$group: {
    _id: '$date',
    LeastActiveDay: {
     $sum: '$active_reservations'
    }
   }}, {$sort: {
    LeastActiveDay: 1
   }}, {$set: {
    date: '$_id'
   }}, {$project: {
    _id: 0,
    LeastActiveDay: '$date',
    With: {
     $concat: [
      {
       $toString: '$LeastActiveDay'
      },
      ' families'
     ]
    }
   }}, {$limit: 1}]
).pretty()