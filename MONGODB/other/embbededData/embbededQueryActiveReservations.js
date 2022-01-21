db.atelier.aggregate(
[{$unwind: {
    path: '$reservations'
   }}, {$match: {
    'reservations.state': 'Active'
   }}, {$group: {
    _id: '$date',
    nOfActive: {
     $sum: 1
    }
   }}, {$addFields: {
    active_reservations: '$nOfActive'
   }}])
.pretty()