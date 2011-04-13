# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Herd'
        db.create_table('euscan_herd', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('herd', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('euscan', ['Herd'])

        # Adding model 'Maintainer'
        db.create_table('euscan_maintainer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('euscan', ['Maintainer'])

        # Adding unique constraint on 'Maintainer', fields ['name', 'email']
        db.create_unique('euscan_maintainer', ['name', 'email'])

        # Adding model 'Package'
        db.create_table('euscan_package', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('homepage', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
        ))
        db.send_create_signal('euscan', ['Package'])

        # Adding unique constraint on 'Package', fields ['category', 'name']
        db.create_unique('euscan_package', ['category', 'name'])

        # Adding M2M table for field herds on 'Package'
        db.create_table('euscan_package_herds', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('package', models.ForeignKey(orm['euscan.package'], null=False)),
            ('herd', models.ForeignKey(orm['euscan.herd'], null=False))
        ))
        db.create_unique('euscan_package_herds', ['package_id', 'herd_id'])

        # Adding M2M table for field maintainers on 'Package'
        db.create_table('euscan_package_maintainers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('package', models.ForeignKey(orm['euscan.package'], null=False)),
            ('maintainer', models.ForeignKey(orm['euscan.maintainer'], null=False))
        ))
        db.create_unique('euscan_package_maintainers', ['package_id', 'maintainer_id'])

        # Adding model 'Version'
        db.create_table('euscan_version', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['euscan.Package'])),
            ('slot', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('packaged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('overlay', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('urls', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('euscan', ['Version'])

        # Adding unique constraint on 'Version', fields ['package', 'slot', 'revision', 'version']
        db.create_unique('euscan_version', ['package_id', 'slot', 'revision', 'version'])

        # Adding model 'EuscanResult'
        db.create_table('euscan_euscanresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['euscan.Package'])),
            ('startdate', self.gf('django.db.models.fields.DateTimeField')()),
            ('endstate', self.gf('django.db.models.fields.DateTimeField')()),
            ('result', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('euscan', ['EuscanResult'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Version', fields ['package', 'slot', 'revision', 'version']
        db.delete_unique('euscan_version', ['package_id', 'slot', 'revision', 'version'])

        # Removing unique constraint on 'Package', fields ['category', 'name']
        db.delete_unique('euscan_package', ['category', 'name'])

        # Removing unique constraint on 'Maintainer', fields ['name', 'email']
        db.delete_unique('euscan_maintainer', ['name', 'email'])

        # Deleting model 'Herd'
        db.delete_table('euscan_herd')

        # Deleting model 'Maintainer'
        db.delete_table('euscan_maintainer')

        # Deleting model 'Package'
        db.delete_table('euscan_package')

        # Removing M2M table for field herds on 'Package'
        db.delete_table('euscan_package_herds')

        # Removing M2M table for field maintainers on 'Package'
        db.delete_table('euscan_package_maintainers')

        # Deleting model 'Version'
        db.delete_table('euscan_version')

        # Deleting model 'EuscanResult'
        db.delete_table('euscan_euscanresult')


    models = {
        'euscan.euscanresult': {
            'Meta': {'object_name': 'EuscanResult'},
            'endstate': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['euscan.Package']"}),
            'result': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {})
        },
        'euscan.herd': {
            'Meta': {'object_name': 'Herd'},
            'herd': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'euscan.maintainer': {
            'Meta': {'unique_together': "(['name', 'email'],)", 'object_name': 'Maintainer'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'euscan.package': {
            'Meta': {'unique_together': "(['category', 'name'],)", 'object_name': 'Package'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'herds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['euscan.Herd']", 'symmetrical': 'False', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['euscan.Maintainer']", 'symmetrical': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'euscan.version': {
            'Meta': {'unique_together': "(['package', 'slot', 'revision', 'version'],)", 'object_name': 'Version'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overlay': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['euscan.Package']"}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'urls': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['euscan']
