db.families.aggregate(
[{$unwind: {
    path: '$reservations'
    }}, {$group: {
    _id: null,
    TotalNumberElements: {
        $sum: '$reservations.family.numberElements'
    },
    AVGNE: {
        $avg: '$reservations.family.numberElements'
    }
    }}, {$project: {
    _id: 0,
    TotalNumberElements: 1,
    AverageNumberElementsPerFamily: {
        $round: [
        '$AVGNE',
        1
        ]
    }
}}]
).pretty()