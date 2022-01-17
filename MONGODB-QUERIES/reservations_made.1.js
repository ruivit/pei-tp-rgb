db.atelier.aggregate(
    [{$group: {
        _id: null,
        total_active_reservations: {
         $sum: '$active_reservations'
        },
        total_canceled_reservations: {
         $sum: '$canceled_reservations'
        }
       }}, 

       {$project: {
        _id: 0,
        total_reservations: {
         $add: [
          '$total_active_reservations',
          '$total_canceled_reservations'
         ]
        },
        total_active_reservations: '$total_active_reservations',
        total_canceled_reservations: '$total_canceled_reservations'
       }}]
).pretty()
