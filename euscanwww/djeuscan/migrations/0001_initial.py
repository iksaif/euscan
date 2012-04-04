# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Herd'
        db.create_table('djeuscan_herd', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('herd', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('djeuscan', ['Herd'])

        # Adding model 'Maintainer'
        db.create_table('djeuscan_maintainer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('email', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('djeuscan', ['Maintainer'])

        # Adding model 'Package'
        db.create_table('djeuscan_package', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('homepage', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('n_versions', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_packaged', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_overlay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_version_gentoo', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_version_gentoo', null=True, to=orm['djeuscan.Version'])),
            ('last_version_overlay', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_version_overlay', null=True, to=orm['djeuscan.Version'])),
            ('last_version_upstream', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_version_upstream', null=True, to=orm['djeuscan.Version'])),
        ))
        db.send_create_signal('djeuscan', ['Package'])

        # Adding unique constraint on 'Package', fields ['category', 'name']
        db.create_unique('djeuscan_package', ['category', 'name'])

        # Adding M2M table for field herds on 'Package'
        db.create_table('djeuscan_package_herds', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('package', models.ForeignKey(orm['djeuscan.package'], null=False)),
            ('herd', models.ForeignKey(orm['djeuscan.herd'], null=False))
        ))
        db.create_unique('djeuscan_package_herds', ['package_id', 'herd_id'])

        # Adding M2M table for field maintainers on 'Package'
        db.create_table('djeuscan_package_maintainers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('package', models.ForeignKey(orm['djeuscan.package'], null=False)),
            ('maintainer', models.ForeignKey(orm['djeuscan.maintainer'], null=False))
        ))
        db.create_unique('djeuscan_package_maintainers', ['package_id', 'maintainer_id'])

        # Adding model 'Version'
        db.create_table('djeuscan_version', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djeuscan.Package'])),
            ('slot', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('packaged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('overlay', self.gf('django.db.models.fields.CharField')(default='gentoo', max_length=128, db_index=True)),
            ('urls', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('alive', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
        ))
        db.send_create_signal('djeuscan', ['Version'])

        # Adding unique constraint on 'Version', fields ['package', 'slot', 'revision', 'version', 'overlay']
        db.create_unique('djeuscan_version', ['package_id', 'slot', 'revision', 'version', 'overlay'])

        # Adding model 'VersionLog'
        db.create_table('djeuscan_versionlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djeuscan.Package'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('slot', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('packaged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('overlay', self.gf('django.db.models.fields.CharField')(default='gentoo', max_length=128)),
            ('action', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('djeuscan', ['VersionLog'])

        # Adding model 'EuscanResult'
        db.create_table('djeuscan_euscanresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djeuscan.Package'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('result', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('djeuscan', ['EuscanResult'])

        # Adding model 'Log'
        db.create_table('djeuscan_log', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('n_packages_gentoo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_packages_overlay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_packages_outdated', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_gentoo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_overlay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_upstream', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('djeuscan', ['Log'])

        # Adding model 'WorldLog'
        db.create_table('djeuscan_worldlog', (
            ('log_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['djeuscan.Log'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('djeuscan', ['WorldLog'])

        # Adding model 'CategoryLog'
        db.create_table('djeuscan_categorylog', (
            ('log_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['djeuscan.Log'], unique=True, primary_key=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('djeuscan', ['CategoryLog'])

        # Adding model 'HerdLog'
        db.create_table('djeuscan_herdlog', (
            ('log_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['djeuscan.Log'], unique=True, primary_key=True)),
            ('herd', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djeuscan.Herd'])),
        ))
        db.send_create_signal('djeuscan', ['HerdLog'])

        # Adding model 'MaintainerLog'
        db.create_table('djeuscan_maintainerlog', (
            ('log_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['djeuscan.Log'], unique=True, primary_key=True)),
            ('maintainer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djeuscan.Maintainer'])),
        ))
        db.send_create_signal('djeuscan', ['MaintainerLog'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Version', fields ['package', 'slot', 'revision', 'version', 'overlay']
        db.delete_unique('djeuscan_version', ['package_id', 'slot', 'revision', 'version', 'overlay'])

        # Removing unique constraint on 'Package', fields ['category', 'name']
        db.delete_unique('djeuscan_package', ['category', 'name'])

        # Deleting model 'Herd'
        db.delete_table('djeuscan_herd')

        # Deleting model 'Maintainer'
        db.delete_table('djeuscan_maintainer')

        # Deleting model 'Package'
        db.delete_table('djeuscan_package')

        # Removing M2M table for field herds on 'Package'
        db.delete_table('djeuscan_package_herds')

        # Removing M2M table for field maintainers on 'Package'
        db.delete_table('djeuscan_package_maintainers')

        # Deleting model 'Version'
        db.delete_table('djeuscan_version')

        # Deleting model 'VersionLog'
        db.delete_table('djeuscan_versionlog')

        # Deleting model 'EuscanResult'
        db.delete_table('djeuscan_euscanresult')

        # Deleting model 'Log'
        db.delete_table('djeuscan_log')

        # Deleting model 'WorldLog'
        db.delete_table('djeuscan_worldlog')

        # Deleting model 'CategoryLog'
        db.delete_table('djeuscan_categorylog')

        # Deleting model 'HerdLog'
        db.delete_table('djeuscan_herdlog')

        # Deleting model 'MaintainerLog'
        db.delete_table('djeuscan_maintainerlog')


    models = {
        'djeuscan.categorylog': {
            'Meta': {'object_name': 'CategoryLog', '_ormbases': ['djeuscan.Log']},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        },
        'djeuscan.euscanresult': {
            'Meta': {'object_name': 'EuscanResult'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'result': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'djeuscan.herd': {
            'Meta': {'object_name': 'Herd'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'herd': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'djeuscan.herdlog': {
            'Meta': {'object_name': 'HerdLog', '_ormbases': ['djeuscan.Log']},
            'herd': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Herd']"}),
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        },
        'djeuscan.log': {
            'Meta': {'object_name': 'Log'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'n_packages_gentoo': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packages_outdated': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packages_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions_gentoo': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions_upstream': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'djeuscan.maintainer': {
            'Meta': {'object_name': 'Maintainer'},
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djeuscan.maintainerlog': {
            'Meta': {'object_name': 'MaintainerLog', '_ormbases': ['djeuscan.Log']},
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'}),
            'maintainer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Maintainer']"})
        },
        'djeuscan.package': {
            'Meta': {'unique_together': "(['category', 'name'],)", 'object_name': 'Package'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'herds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Herd']", 'symmetrical': 'False', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_version_gentoo': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_gentoo'", 'null': 'True', 'to': "orm['djeuscan.Version']"}),
            'last_version_overlay': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_overlay'", 'null': 'True', 'to': "orm['djeuscan.Version']"}),
            'last_version_upstream': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_upstream'", 'null': 'True', 'to': "orm['djeuscan.Version']"}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Maintainer']", 'symmetrical': 'False', 'blank': 'True'}),
            'n_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packaged': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djeuscan.version': {
            'Meta': {'unique_together': "(['package', 'slot', 'revision', 'version', 'overlay'],)", 'object_name': 'Version'},
            'alive': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overlay': ('django.db.models.fields.CharField', [], {'default': "'gentoo'", 'max_length': '128', 'db_index': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'urls': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djeuscan.versionlog': {
            'Meta': {'object_name': 'VersionLog'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overlay': ('django.db.models.fields.CharField', [], {'default': "'gentoo'", 'max_length': '128'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djeuscan.worldlog': {
            'Meta': {'object_name': 'WorldLog', '_ormbases': ['djeuscan.Log']},
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['djeuscan']
