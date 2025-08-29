<template>
  <div class="view">
    <Panel :title="$t('m.Choice_Question_List')">
      <div slot="header">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-button type="primary" size="small" @click="goCreateChoiceQuestion" icon="el-icon-plus">{{$t('m.Create')}}</el-button>
          </el-col>
          <el-col :span="8">
            <el-input v-model="keyword" prefix-icon="el-icon-search" placeholder="Keywords"></el-input>
          </el-col>
          <el-col :span="8">
            <el-button type="primary" size="small" @click="filterByKeyword">{{$t('m.Search')}}</el-button>
          </el-col>
        </el-row>
      </div>
      <el-table
        v-loading="loadingTable"
        element-loading-text="loading"
        ref="table"
        :data="choiceQuestionList"
        style="width: 100%">
        <el-table-column width="100" prop="id" label="ID"></el-table-column>
        <el-table-column prop="title" label="Title">
          <template slot-scope="{row}">
            <a @click="goEdit(row.id)" class="entry">{{ row.title }}</a>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="Difficulty" width="150">
          <template slot-scope="scope">
            <el-tag :type="scope.row.difficulty === 'Easy' ? 'success' : scope.row.difficulty === 'Medium' ? 'warning' : 'danger'" size="small">
              {{ scope.row.difficulty }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by.username" label="Author" width="150"></el-table-column>
        <el-table-column prop="create_time" label="Create Time" width="200">
          <template slot-scope="scope">
            {{ scope.row.create_time | localtime }}
          </template>
        </el-table-column>
        <el-table-column prop="visible" label="Visible" width="100">
          <template slot-scope="scope">
            <el-switch v-model="scope.row.visible" @change="updateChoiceQuestion(scope.row)"></el-switch>
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="Operation" width="200">
          <template slot-scope="scope">
            <icon-btn name="Edit" icon="edit" @click.native="goEdit(scope.row.id)"></icon-btn>
            <icon-btn name="Delete" icon="trash" @click.native="deleteChoiceQuestion(scope.row.id)"></icon-btn>
          </template>
        </el-table-column>
      </el-table>
      <div class="panel-options">
        <el-pagination
          class="page"
          layout="prev, pager, next"
          @current-change="currentChange"
          :page-size="pageSize"
          :total="total">
        </el-pagination>
      </div>
    </Panel>
  </div>
</template>

<script>
  import api from '../../api.js'

  export default {
    name: 'ChoiceQuestionList',
    data () {
      return {
        pageSize: 10,
        total: 0,
        choiceQuestionList: [],
        keyword: '',
        loadingTable: false,
        currentPage: 1
      }
    },
    mounted () {
      this.getChoiceQuestionList(1)
    },
    methods: {
      // 切换页码回调
      currentChange (page) {
        this.currentPage = page
        this.getChoiceQuestionList(page)
      },
      getChoiceQuestionList (page) {
        this.loadingTable = true
        api.getChoiceQuestionList((page - 1) * this.pageSize, this.pageSize, this.keyword).then(res => {
          this.loadingTable = false
          this.total = res.data.data.total
          this.choiceQuestionList = res.data.data.results
        }, res => {
          this.loadingTable = false
        })
      },
      goEdit (choiceQuestionId) {
        this.$router.push({name: 'edit-choice-question', params: {choiceQuestionId}})
      },
      goCreateChoiceQuestion () {
        this.$router.push({name: 'create-choice-question'})
      },
      deleteChoiceQuestion (id) {
        this.$confirm('Sure to delete this choice question? The associated submissions will be deleted as well.', 'Delete Choice Question', {
          type: 'warning'
        }).then(() => {
          api.deleteChoiceQuestion(id).then(() => [
            this.getChoiceQuestionList(this.currentPage)
          ]).catch(() => {
          })
        }, () => {
        })
      },
      filterByKeyword () {
        this.currentPage = 1
        this.getChoiceQuestionList(1)
      },
      updateChoiceQuestion (row) {
        api.editChoiceQuestion(row).then(res => {
          this.$success('Updated successfully')
        }).catch(() => {
        })
      }
    }
  }
</script>

<style scoped lang="less">
  .entry {
    color: #495060;
    &:hover {
      color: #2d8cf0;
      border-bottom: 1px solid #2d8cf0;
    }
  }
</style>