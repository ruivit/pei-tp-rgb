db.atelier.aggregate(
[{$match: {
    'reservations.state': 'Active'
   }}, {$group: {
    _id: '$date',
    TotalFamiliesPerDay: {
     $sum: {
      $subtract: [
       50,
       '$slots'
      ]
     }
    }
   }}]
).pretty()