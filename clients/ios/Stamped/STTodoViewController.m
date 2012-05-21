//
//  STTodoViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/19/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTodoViewController.h"
#import "STStampedAPI.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STDebug.h"
#import "ECSlidingViewController.h"

@interface STTodoCell : UITableViewCell

- (id)initWithTodo:(id<STTodo>)todo;

@end

@implementation STTodoCell

- (id)initWithTodo:(id<STTodo>)todo {
  self = [super initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:@"test"];
  if (self) {
    self.textLabel.text = todo.entity.title;
  }
  return self;
}

@end

@interface STTodoViewController () <UITableViewDelegate, UITableViewDataSource>

@property (nonatomic, readonly, retain) NSMutableArray* todos;

@end

@implementation STTodoViewController

@synthesize todos = todos_;

static STTodoViewController* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STTodoViewController alloc] init];
}

+ (STTodoViewController*)sharedInstance {
  return _sharedInstance;
}

- (id)init
{
  self = [super initWithHeaderHeight:0];
  if (self) {
    todos_ = [[NSMutableArray alloc] init];
  }
  return self;
}

- (void)backButtonClicked:(id)button {
  [self.slidingViewController anchorTopViewTo:ECRight];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  self.tableView.delegate = self;
  self.tableView.dataSource = self;
  [self reloadStampedData];
  self.navigationItem.leftBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Home"
                                                                            style:UIBarButtonItemStyleDone
                                                                           target:self 
                                                                           action:@selector(backButtonClicked:)] autorelease];
  [STDebug log:@"To-Do is still pre-alpha"];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  if (self.todos) {
    return self.todos.count;
  }
  return 0;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  id<STTodo> todo = [self.todos objectAtIndex:indexPath.row];
  return [[[STTodoCell alloc] initWithTodo:todo] autorelease];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  id<STTodo> todo = [self.todos objectAtIndex:indexPath.row];
  STActionContext* context = [STActionContext context];
  id<STAction> action = [STStampedActions actionViewEntity:todo.entity.entityID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)reloadStampedData {
  [self.todos removeAllObjects];
  STGenericCollectionSlice* slice = [[[STGenericCollectionSlice alloc] init] autorelease];
  slice.offset = [NSNumber numberWithInteger:0];
  slice.limit = [NSNumber numberWithInteger:20];
  [self loadMoreWithSlice:slice];
}

- (void)loadMoreWithSlice:(STGenericCollectionSlice*)slice {
  STGenericCollectionSlice* nextSlice = [slice resizedSliceWithLimit:slice.limit andOffset:[NSNumber numberWithInteger:slice.offset.integerValue + slice.limit.integerValue]];
  [[STStampedAPI sharedInstance] todosWithGenericCollectionSlice:slice andCallback:^(NSArray<STTodo>* todoes, NSError* error) {
    if (todoes.count > 0) {
      [self.todos addObjectsFromArray:todoes];
      [self.tableView reloadData];
      [self loadMoreWithSlice:nextSlice];
    }
  }];
}

@end
