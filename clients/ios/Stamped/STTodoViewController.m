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
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"

typedef enum STTodoState {
STTodoStateDone,
STTodoStateUndone,
STTodoStateStamped,
} STTodoState;

static NSString* const _todoReuseIdentifier = @"todo-cell";

@protocol STTodoCellDelegate <NSObject>

- (void)clickedImageForTodo:(id<STTodo>)todo;

@end


@interface STTodoViewController () <UITableViewDelegate, UITableViewDataSource, STTodoCellDelegate, UIActionSheetDelegate>

@property (nonatomic, readonly, retain) NSMutableArray* todos;
@property (nonatomic, readwrite, retain) STCancellation* pending;
@property (nonatomic, readwrite, assign) BOOL finished;
@property (nonatomic, readwrite, retain) id<STTodo> actionSheetTodo;
@property (nonatomic, readonly, retain) NSMutableSet* cancellations;

+ (STTodoState)todoState:(id<STTodo>)todo;

@end

@interface STTodoCell : UITableViewCell

- (void)setupWithTodo:(id<STTodo>)todo;

@property (nonatomic, readonly, retain) UIImageView* checkView;
@property (nonatomic, readonly, retain) UILabel* titleView;
@property (nonatomic, readonly, retain) UIImageView* categoryImageView;
@property (nonatomic, readonly, retain) UILabel* subtitleView;
@property (nonatomic, readwrite, retain) id<STTodo> todo;
@property (nonatomic, readwrite, assign) id<STTodoCellDelegate> delegate;

@end

@implementation STTodoCell

@synthesize checkView = _checkView;
@synthesize titleView = _titleView;
@synthesize categoryImageView = _categoryImageView;
@synthesize subtitleView = _subtitleView;
@synthesize todo = _todo;
@synthesize delegate = _delegate;

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
        
        UIView* tapButton = [Util tapViewWithFrame:_checkView.frame target:self selector:@selector(iconClicked:) andMessage:nil];
        _subtitleView = [[UILabel alloc] initWithFrame:CGRectMake(82, yOffset - 1, 0, 0)];
        _subtitleView.font = [UIFont stampedFontWithSize:10];
        _subtitleView.textColor = [UIColor stampedGrayColor];
        _subtitleView.textAlignment = UITextAlignmentLeft;
        _subtitleView.lineBreakMode = UILineBreakModeTailTruncation;
        
        [self.contentView addSubview:_checkView];
        [self.contentView addSubview:_titleView];
        [self.contentView addSubview:_categoryImageView];
        [self.contentView addSubview:_subtitleView];
        [self.contentView addSubview:tapButton];
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

- (void)iconClicked:(id)notImportant {
    [self.delegate clickedImageForTodo:self.todo];
}

- (void)setupWithTodo:(id<STTodo>)todo {
    id<STEntity> entity = todo.source.entity;
    _titleView.text = entity.title;
    [_titleView sizeToFit];
    if (_titleView.frame.size.width > 225) {
        CGRect frame = _titleView.frame;
        frame.size.width = 225;
        _titleView.frame = frame;
    }
    _subtitleView.text = entity.subtitle;
    _subtitleView.textColor = [todo.complete boolValue] ? [UIColor stampedLightGrayColor] : [UIColor stampedGrayColor];
    [_subtitleView sizeToFit];
    if (_subtitleView.frame.size.width > 200) {
        CGRect frame = _subtitleView.frame;
        frame.size.width = 200;
        _subtitleView.frame = frame;
    }
    _categoryImageView.image = [Util imageForCategory:entity.category];
    NSString* imageName = nil;
    STTodoState state = [STTodoViewController todoState:todo];
    if (state == STTodoStateStamped) {
        imageName = @"TEMP_todo_done";
    }
    else if (state == STTodoStateDone) {
        imageName = @"TEMP_todo_finished";
    }
    else {
        imageName = @"TEMP_todo_not_done";
    }
    _checkView.image = [UIImage imageNamed:imageName];
    self.todo = todo;
}

@end

@implementation STTodoViewController

@synthesize todos = todos_;
@synthesize pending = _pending;
@synthesize finished = _finished;
@synthesize actionSheetTodo = _actionSheetTodo;
@synthesize cancellations = _cancellations;

- (id)init
{
    self = [super init];
    if (self) {
        todos_ = [[NSMutableArray alloc] init];
        _cancellations = [[NSMutableSet alloc] init];
    }
    return self;
}

- (void)cancelPendingOps {
    [_pending cancel];
    for (STCancellation* cancellation in _cancellations) {
        [cancellation cancel];
    }
    [_cancellations removeAllObjects];
}

- (void)dealloc
{
    [self cancelPendingOps];
    [todos_ release];
    [_pending release];
    [_actionSheetTodo release];
    [_cancellations release];
    [super dealloc];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    self.tableView.separatorColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
    
    [Util addHomeButtonToController:self withBadge:YES];
    [Util addCreateStampButtonToController:self];
    
    [self reloadDataSource];
    //self.showsSearchBar = NO;
}

- (void)viewDidUnload
{
    [super viewDidUnload];
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
    [self cancelPendingOps];
}

+ (STTodoState)todoState:(id<STTodo>)todo {
    if (todo.stampID) {
        return STTodoStateStamped;
    }
    else if (todo.complete.boolValue) {
        return STTodoStateDone;
    }
    else {
        return STTodoStateUndone;
    }
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
    }
    [cell setupWithTodo:todo];
    cell.delegate = self;
    return cell;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
    id<STTodo> todo = [self.todos objectAtIndex:indexPath.row];
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewEntity:todo.source.entity.entityID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
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
            [self dataSourceDidFinishLoading];
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


#pragma mark - UIActionSheetDelegate

- (void)_stampIt:(id<STTodo>)todo {
    NSMutableArray<STUser>* credits = [NSMutableArray array];
    if (todo.previews.credits.count) {
        for (id<STStampPreview> credit in todo.previews.credits) {
            if (credit.user) {
                [credits addObject:credit.user];
                //NSLog(@"Has a credit: %@", credit.user.screenName);
            }
        }
    }
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewCreateStampWithEntity:todo.source.entity creditedUsers:credits withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)_setComplete:(id<STTodo>)todo value:(BOOL)complete {
    STCancellation* cancellation = [[STStampedAPI sharedInstance] setTodoCompleteWithEntityID:todo.source.entity.entityID
                                                                                     complete:complete
                                                                                  andCallback:^(id<STTodo> todo, NSError *error, STCancellation *cancellation) {
                                                                                      if (todo) {
                                                                                          [self reloadDataSource];
                                                                                      }
                                                                                      else {
                                                                                          [Util warnWithMessage:@"Could not complete operation" andBlock:nil];
                                                                                      }
                                                                                  }];
    [self.cancellations addObject:cancellation];
}

- (void)actionSheet:(UIActionSheet *)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
    STTodoState state = [STTodoViewController todoState:self.actionSheetTodo];
    id<STTodo> todo = self.actionSheetTodo;
    self.actionSheetTodo = nil;
    if (state == STTodoStateDone) {
        //otherButtonTitles = [NSArray arrayWithObjects:@"Mark as undone", @"Stamp it", nil];
        if (buttonIndex == 0) {
            [self _setComplete:todo value:NO];
        }
        else if (buttonIndex == 1) {
            [self _stampIt:todo];
        }
    }
    else if (state == STTodoStateStamped) {
        //otherButtonTitles = [NSArray arrayWithObject:@"View stamp"];
        if (buttonIndex == 0) {
            NSString* stampID = todo.stampID;
            [[STStampedActions sharedInstance] viewStampWithStampID:stampID];
        }
    }
    else {
        //otherButtonTitles = [NSArray arrayWithObjects:@"Mark as done", @"Stamp it", nil];
        if (buttonIndex == 0) {
            [self _setComplete:todo value:YES];
        }
        else if (buttonIndex == 1) {
            [self _stampIt:todo];
        }
    }
}

#pragma mark - STTodoCellDelegate

- (void)clickedImageForTodo:(id<STTodo>)todo {
    self.actionSheetTodo = todo;
    
    NSArray* otherButtonTitles = nil;
    STTodoState state = [STTodoViewController todoState:todo];
    if (state == STTodoStateDone) {
        otherButtonTitles = [NSArray arrayWithObjects:@"Mark as undone", @"Stamp it", nil];
    }
    else if (state == STTodoStateStamped) {
        otherButtonTitles = [NSArray arrayWithObject:@"View stamp"];
    }
    else {
        otherButtonTitles = [NSArray arrayWithObjects:@"Mark as done", @"Stamp it", nil];
    }
    
    UIActionSheet *actionSheet = nil;
    if (otherButtonTitles.count == 1) {
        actionSheet = [[UIActionSheet alloc] initWithTitle:nil
                                                  delegate:self 
                                         cancelButtonTitle:@"Cancel" 
                                    destructiveButtonTitle:nil 
                                         otherButtonTitles:[otherButtonTitles objectAtIndex:0], nil];
    }
    else {
        actionSheet = [[UIActionSheet alloc] initWithTitle:nil
                                                  delegate:self 
                                         cancelButtonTitle:@"Cancel" 
                                    destructiveButtonTitle:nil 
                                         otherButtonTitles:[otherButtonTitles objectAtIndex:0], [otherButtonTitles objectAtIndex:1], nil];
    }
    actionSheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
    [actionSheet showInView:self.view];
    [actionSheet release];
}

@end
