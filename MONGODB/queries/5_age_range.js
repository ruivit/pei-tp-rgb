db.atelier.aggregate(
[{
    $unwind: {
        path: '$reservations'
    }
}, {
        $unwind: {
            path: '$reservations.family.familyElement'
        }
    }, {
        $match: {
            'reservations.state': 'Active'
        }
    }, {
        $addFields: {
            age: '$reservations.family.familyElement.age_when_visiting'
        }
    }, {
        $group: {
            "_id": {
                "$concat": [
                    { "$cond": [{ "$lte": ["$age", 0] }, "Unknown", ""] },
                    { "$cond": [{ "$and": [{ "$gt": ["$age", 0] }, { "$lt": ["$age", 2] }] }, "Under 2", ""] },
                    { "$cond": [{ "$and": [{ "$gte": ["$age", 2] }, { "$lte": ["$age", 6] }] }, "2 - 6", ""] },
                    { "$cond": [{ "$and": [{ "$gte": ["$age", 7] }, { "$lte": ["$age", 12] }] }, "7 - 12", ""] },
                    { "$cond": [{ "$and": [{ "$gte": ["$age", 13] }, { "$lte": ["$age", 18] }] }, "13 - 18", ""] },
                    { "$cond": [{ "$and": [{ "$gte": ["$age", 19] }, { "$lte": ["$age", 24] }] }, "19 - 24", ""] },
                    { "$cond": [{ "$and": [{ "$gte": ["$age", 25] }, { "$lte": ["$age", 30] }] }, "25 - 30", ""] },
                    { "$cond": [{ "$and": [{ "$gte": ["$age", 31] }, { "$lte": ["$age", 40] }] }, "31 - 40", ""] },
                    { "$cond": [{ "$and": [{ "$gte": ["$age", 41] }, { "$lte": ["$age", 60] }] }, "41 - 60", ""] },
                    { "$cond": [{ "$gte": [{ "$gte": ["$age", 61] }, { "$lte": ["$age", 100] }] }, "Over 60", ""] }
                ]
            },
            "sum": { "$sum": 1 }
        }
    }, {
        $project: {
            _id: 0,
            age: '$_id',
            number_of_people: '$sum'
        }
    }]
).pretty()
