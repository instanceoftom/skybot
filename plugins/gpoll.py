'''

Poll a string
 	
by instanceoftom
'''

from util import hook,http
import ast


def db_init(db):
    db.execute("create table if not exists gpoll"
                "(poll_name,chan,poll_creator,"
                "primary key(poll_name,chan))")
    db.execute("create table if not exists gpoll_choices"
                "(poll_name,chan, poll_choice,"
                "primary key(poll_name,chan,poll_choice))")

    db.execute("create table if not exists gpoll_votes"
                "(poll_name,chan, user_name, poll_choice,"
                "primary key(poll_name,chan,user_name))")
    db.commit()

    return db

def get_creator(db, poll_name,chan):
    print poll_name
    row = db.execute("select poll_name,poll_creator from gpoll where poll_name=? and chan=?",[poll_name]).fetchall()
    if row:
        return row[0]
    else:
        return None

def get_choices(db, poll_name,chan):
    rows = db.execute("select poll_choice from gpoll_choices where poll_name=? and chan=?",
                      [poll_name,chan]).fetchall()

    if rows:

        choices = ""
        for row in rows:
            choices += "'%s', " % (row[0],)
        message = "Choices for %s: %s" % (poll_name,choices)
        return message
    else:
        return "Poll '%s' does not exist" % (poll_name,)


def get_vote_summary(db,poll_name,chan):
    rows = db.execute("select poll_choice,count(poll_choice) from gpoll_votes where poll_name=? and chan=? group by poll_choice",
                      [poll_name,chan]).fetchall()
    if rows:
        return rows
    else:
        return None

@hook.command('gpollchoices')
def choices(inp,nick='',chan='',db=None):
    return get_choices(db,inp,chan)

@hook.command
def vote(inp,nick='',chan='',db=None):
    "uh"
    db_init(db)
    
    try:
        poll_name,vote = inp.split(None,1)
    except ValueError:
        return vote.__doc__

    row = db.execute("select count(*) from gpoll_choices where poll_name=? and chan=? and poll_choice=?",
                      [poll_name,chan,vote]).fetchone()
    if row:
        if row[0] > 0:
            print row[0]
            db.execute("replace into gpoll_votes(poll_name,chan,user_name,poll_choice) values"
               "(?,?,?,?)", (poll_name,chan,nick, vote))
            db.commit()
            return "vote added."
        else:
        	return get_choices(db,poll_name,chan)



@hook.command('gpollstats')
def get_poll_stats(inp, nick='', chan='', db=None):
    ".gpoll dude"
    print "get_poll_stats called"
    db_init(db)
    return get_vote_summary(db,inp,chan)



@hook.command
def gpoll(inp, nick='', chan='', db=None):
    ".gpoll dude"
    db_init(db)

    try:
        terms = inp.split(None)
        poll_name=  terms[0]
        terms = terms[1:]
    except ValueError:
        return gpoll.__doc__
 #   data = get_memory(db, chan, poll_name)

    db.execute("replace into gpoll(poll_name,chan,poll_creator) values"
               " (?,?,?)", (poll_name,chan, nick))
    
    for term in terms:
        db.execute("replace into gpoll_choices(poll_name,chan,poll_choice) values"
               "(?,?,?)", (poll_name,chan, term))

    db.commit()
    data = get_choices(db, poll_name,chan)
    if data:
        return  data
    else:
        return 'meh.'


@hook.command
def clearallpolls(inp, nick='', chan='', db=None):
	db_init(db)
	db.execute("delete from gpoll where poll_name like '%'")
	db.commit()