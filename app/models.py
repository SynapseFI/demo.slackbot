"""SQLAlchemy model class definitions."""
from synapse_pay_rest import User as SynapseUser
from synapse_pay_rest.models.nodes import AchUsNode, SynapseUsNode
from config import db
from synapse_client import synapse_client


class User(db.Model):
    """Stores Slack user id with Synapse user id and node info."""
    __tablename__ = 'users'
    slack_user_id = db.Column(db.String(15), primary_key=True)
    synapse_user_id = db.Column(db.String(30), unique=True, nullable=False)
    debit_node_id = db.Column(db.String(30), unique=True, nullable=False)
    savings_node_id = db.Column(db.String(30), unique=True, nullable=False)
    recurring_transactions = db.relationship('RecurringTransaction',
                                             backref='user')

    def __init__(self, slack_user_id, synapse_user_id, debit_node_id,
                 savings_node_id):
        self.slack_user_id = slack_user_id
        self.synapse_user_id = synapse_user_id
        self.debit_node_id = debit_node_id
        self.savings_node_id = savings_node_id

    def __repr__(self):
        return '<User: (slack %r), (synapse: %r)>' % (self.slack_user_id,
                                                      self.synapse_user_id)

    @classmethod
    def from_slack_id(cls, slack_user_id):
        return cls.query.filter_by(slack_user_id=slack_user_id).first()

    @classmethod
    def from_request(cls, slack_id, request):
        synapse_user = cls.create_synapse_user(slack_id, request)
        cls.submit_cip(synapse_user, request)
        debit_node = cls.create_debit_node(synapse_user, request)
        savings_node = cls.create_savings_node(synapse_user, request)
        user = cls(slack_id, synapse_user.id, debit_node.id, savings_node.id)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def create_synapse_user(slack_id, request):
        """Creates a new user with Synapse."""
        # 'options' actually required until pending API update or lib change
        options = {
            'note': 'created by Synapse Slackbot',
            'supp_id': slack_id,
            'is_business': False,
            'cip_tag': 1
        }

        return SynapseUser.create(
            client=synapse_client,
            email=request.form['email'],
            phone_number=request.form['phone'],
            legal_name=request.form['name'].title(),
            **options
        )

    @staticmethod
    def submit_cip(synapse_user, request):
        """Uploads CIP base document, photo ID, and SSN for user to Synapse."""
        year, month, day = request.form['birthday'].split('-')
        base_doc = synapse_user.add_base_document(
            ip='127.0.0.1',
            name=request.form['name'],
            alias=request.form['name'],
            birth_day=int(day),
            birth_month=int(month),
            birth_year=int(year),
            email=request.form['email'],
            phone_number=request.form['phone'],
            entity_type='NOT_KNOWN',
            entity_scope='Not Known',
            address_street=request.form['address_street'],
            address_city=request.form['address_city'],
            address_subdivision=request.form['address_state'].upper(),
            address_postal_code=request.form['address_zip'],
            address_country_code='US')
        base_doc.add_virtual_document(type='SSN', value=request.form['ssn'])
        img_file = request.files['govt_id']
        base_doc.add_physical_document(type='GOVT_ID',
                                       mime_type=img_file.content_type,
                                       byte_stream=img_file.read())

    @staticmethod
    def create_debit_node(synapse_user, request):
        """Creates a node from which to draw funds for savings."""
        return AchUsNode.create(
            synapse_user,
            account_number=request.form['account_number'],
            routing_number=request.form['routing_number'],
            nickname='Synapse Automatic Savings Debit Account',
            account_type='PERSONAL',
            account_class='CHECKING'
        )

    @staticmethod
    def create_savings_node(synapse_user, form_data):
        """Creates an FDIC-insured account at Triumph Bank to deposit savings.
        """
        return SynapseUsNode.create(
            synapse_user,
            nickname='Synapse Automatic Savings Account'
        )


class RecurringTransaction(db.Model):
    """Transaction details for a recurring transaction."""
    __tablename__ = 'recurring_transactions'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    periodicity = db.Column(db.Integer)
    slack_user_id = db.Column(db.String(15),
                              db.ForeignKey('users.slack_user_id'))

    def __init__(self, **kwargs):
        self.amount = kwargs['amount']
        self.periodicity = kwargs['periodicity']
        self.slack_user_id = kwargs['slack_user_id']

    def __repr__(self):
        return ('<RecurringTransaction: %r every %r days (User: %r)' %
                (self.amount, self.periodicity, self.slack_user_id))
