db.atelier.aggregate(
[{$group: {
    _id: '$date',
    MostActiveDay: {
        $sum: '$active_reservations'
    }
    }}, {$sort: {
    MostActiveDay: -1
    }}, {$set: {
    date: '$_id'
    }}, {$project: {
    _id: 0,
    MostActiveDay: '$date',
    With: {
        $concat: [
        {
        $toString: '$MostActiveDay'
        },
        ' families'
        ]
    }
    }}, {$limit: 1}])
.pretty()