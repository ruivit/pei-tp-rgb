db.atelier.aggregate(
[{$unwind: {
    path: '$reservations'
   }}, {$match: {
    'reservations.state': 'Active'
   }}, {$group: {
    _id: '$date',
    peopleInActiveReservations: {
     $sum: '$reservations.family.numberElements'
    }
   }}, {$addFields: {
    people_in_active_reservations: '$peopleInActiveReservations'
   }}, {}]
).pretty()