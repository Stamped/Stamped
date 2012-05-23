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
#import "Util.h"
#import <QuartzCore/QuartzCore.h>

static NSString* const _todoReuseIdentifier = @"todo-cell";

@interface STTodoCell : UITableViewCell

- (void)setupWithTodo:(id<STTodo>)todo;

@property (nonatomic, readonly, retain) UIImageView* checkView;
@property (nonatomic, readonly, retain) UILabel* titleView;
@property (nonatomic, readonly, retain) UIImageView* categoryImageView;
@property (nonatomic, readonly, retain) UILabel* subtitleView;
@property (nonatomic, readwrite, retain) id<STTodo> todo;

@end

@implementation STTodoCell

@synthesize checkView = _checkView;
@synthesize titleView = _titleView;
@synthesize categoryImageView = _categoryImageView;
@synthesize subtitleView = _subtitleView;
@synthesize todo = _todo;

- (id)init {
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:_todoReuseIdentifier];
    if (self) {
        CGFloat xOffset = 69;
        _checkView = [[UIImageView alloc] initWithFrame:CGRectMake(15, 8, 44, 44)];
        CGFloat shadowRadius = 1;
        _checkView.layer.shadowRadius = shadowRadius;
        _checkView.layer.shadowOpacity = .15;
        _checkView.layer.shadowColor = [UIColor blackColor].CGColor;
        _checkView.layer.shadowOffset = CGSizeMake(0, shadowRadius);
        _titleView = [[UILabel alloc] initWithFrame:CGRectMake(xOffset, 10, 225, 26)];
        _titleView.font = [UIFont stampedTitleFontWithSize:28];
        _titleView.textColor = [UIColor stampedBlackColor];
        _titleView.textAlignment = UITextAlignmentLeft;
        _titleView.lineBreakMode = UILineBreakModeTailTruncation;
        
        CGFloat yOffset = 39;
        _categoryImageView = [[UIImageView alloc] initWithFrame:CGRectMake(xOffset, yOffset, 10, 10)];
        _subtitleView = [[UILabel alloc] initWithFrame:CGRectMake(82, yOffset - 1, 0, 0)];
        _subtitleView.font = [UIFont stampedFontWithSize:10];
        _subtitleView.textColor = [UIColor stampedGrayColor];
        _subtitleView.textAlignment = UITextAlignmentLeft;
        _subtitleView.lineBreakMode = UILineBreakModeTailTruncation;
        
        [self addSubview:_checkView];
        [self addSubview:_titleView];
        [self addSubview:_categoryImageView];
        [self addSubview:_subtitleView];
    }
    return self;
}

- (void)dealloc
{
    [_checkView release];
    [_titleView release];
    [_categoryImageView release];
    [_subtitleView release];
    [_todo release];
    [super dealloc];
}

- (void)setupWithTodo:(id<STTodo>)todo {
    id<STEntity> entity = todo.entity;//todo.source.entity;
    _titleView.text = entity.title;
    [_titleView sizeToFit];
    _subtitleView.text = entity.subtitle;
    _subtitleView.textColor = [todo.complete boolValue] ? [UIColor stampedLightGrayColor] : [UIColor stampedGrayColor];
    [_subtitleView sizeToFit];
    _categoryImageView.image = [Util imageForCategory:entity.category];
    NSString* imageName = nil;
    if (todo.stampID) {
        imageName = @"TEMP_todo_done";
    }
    else if ([todo.complete boolValue]) {
        imageName = @"TEMP_todo_finished";
    }
    else {
        imageName = @"TEMP_todo_not_done";
    }
    _checkView.image = [UIImage imageNamed:imageName];
    self.todo = todo;
}

@end

@interface STTodoViewController () <UITableViewDelegate, UITableViewDataSource>

@property (nonatomic, readonly, retain) NSMutableArray* todos;
@property (nonatomic, readwrite, retain) STCancellation* pending;
@property (nonatomic, readwrite, assign) BOOL finished;

@end

@implementation STTodoViewController

@synthesize todos = todos_;
@synthesize pending = _pending;
@synthesize finished = _finished;

static STTodoViewController* _sharedInstance;

- (id)init
{
    self = [super init];
    if (self) {
        todos_ = [[NSMutableArray alloc] init];
    }
    return self;
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    self.tableView.separatorColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
    
    //[Util addHomeButtonToController:self withBadge:YES];
    //[Util addCreateStampButtonToController:self];
    
    //self.showsSearchBar = NO;
}

- (void)viewDidUnload
{
    [super viewDidUnload];
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    [self reloadDataSource];
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

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    return 64;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    id<STTodo> todo = [self.todos objectAtIndex:indexPath.row];
    STTodoCell* cell = [tableView dequeueReusableCellWithIdentifier:_todoReuseIdentifier];
    if (!cell) {
        cell = [[[STTodoCell alloc] init] autorelease];
        NSLog(@"Create cell");
    }
    [cell setupWithTodo:todo];
    return cell;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
    id<STTodo> todo = [self.todos objectAtIndex:indexPath.row];
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewEntity:todo.entity.entityID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    NSLog(@"chose entity");
}


- (void)loadMore {
    if (self.pending || self.finished) {
        return;
    }
    STGenericCollectionSlice* slice = [[[STGenericCollectionSlice alloc] init] autorelease];
    slice.offset = [NSNumber numberWithInteger:self.todos.count];
    slice.limit = [NSNumber numberWithInteger:20];
    self.pending = [[STStampedAPI sharedInstance] todosWithGenericCollectionSlice:slice andCallback:^(NSArray<STTodo>* todos, NSError* error, STCancellation* cancellation) {
        self.pending = nil;
        if (todos.count > 0) {
            [self.todos addObjectsFromArray:todos];
            [self.tableView reloadData];
            [self loadNextPage];
        }
        else {
            self.finished = YES;
            [self.tableView reloadData];
        }
    }];
}

#pragma mark - STRestController 

- (BOOL)dataSourceReloading {
    return self.pending != nil;
}

- (void)loadNextPage {
    [self loadMore];
}

- (BOOL)dataSourceHasMoreData {
    return !self.finished;
}

- (void)reloadDataSource {
    [self.pending cancel];
    self.pending = nil;
    self.finished = NO;
    [self.todos removeAllObjects];
    [self.tableView reloadData];
    [self loadMore];
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return self.todos.count == 0 && self.finished;
}

- (void)setupNoDataView:(NoDataView*)view {
    UILabel* text = [Util viewWithText:@"No todos" 
                                  font:[UIFont stampedBoldFont]
                                 color:[UIColor stampedGrayColor]
                                  mode:UILineBreakModeTailTruncation
                            andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    text.frame = [Util centeredAndBounded:text.frame.size inFrame:CGRectMake(0, 0, view.frame.size.width, view.frame.size.height)];
    //[view addSubview:view];
}

@end
