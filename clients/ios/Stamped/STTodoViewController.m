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
#import "STPreviewsView.h"
#import "STSimplePreviews.h"
#import "STSharedCaches.h"
#import "STObjectSetAccelerator.h"
#import "NoDataUtil.h"

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

@property (nonatomic, readwrite, retain) STCache* cache;
@property (nonatomic, readwrite, retain) STCacheSnapshot* snapshot;
@property (nonatomic, readwrite, assign) BOOL reloading;
@property (nonatomic, readwrite, assign) BOOL dirty;
@property (nonatomic, readwrite, retain) id<STTodo> actionSheetTodo;
@property (nonatomic, readwrite, retain) NSMutableArray* cancellations;

+ (STTodoState)todoState:(id<STTodo>)todo;

@end

@interface STTodoCell : UITableViewCell

- (void)setupWithTodo:(id<STTodo>)todo;

@property (nonatomic, readonly, retain) UIImageView* backgroundGradient;
@property (nonatomic, readonly, retain) UIImageView* checkView;
@property (nonatomic, readonly, retain) UIView* crossOutLine;
@property (nonatomic, readonly, retain) UIImageView* stampImage;
@property (nonatomic, readonly, retain) UILabel* titleView;
@property (nonatomic, readonly, retain) UIImageView* categoryImageView;
@property (nonatomic, readonly, retain) UILabel* subtitleView;
@property (nonatomic, readonly, retain) UIView* todoDots;
@property (nonatomic, readonly, retain) STPreviewsView* previews;
@property (nonatomic, readwrite, retain) id<STTodo> todo;
@property (nonatomic, readwrite, assign) id<STTodoCellDelegate> delegate;
@property (nonatomic, readwrite, assign) BOOL hasPreviews;

@end

@implementation STTodoCell

@synthesize backgroundGradient = _backgroundGradient;
@synthesize checkView = _checkView;
@synthesize crossOutLine = _crossOutLine;
@synthesize stampImage = _stampImage;
@synthesize titleView = _titleView;
@synthesize categoryImageView = _categoryImageView;
@synthesize subtitleView = _subtitleView;
@synthesize todoDots = _todoDots;
@synthesize previews = _previews;
@synthesize todo = _todo;
@synthesize delegate = _delegate;
@synthesize hasPreviews = _hasPreviews;

- (id)init {
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:_todoReuseIdentifier];
    if (self) {
        _backgroundGradient = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"todo_bg"]];
        CGRect bgFrame = _backgroundGradient.frame;
        bgFrame.size.width = 320;
        _backgroundGradient.frame = bgFrame;
        
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
        
        _crossOutLine = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 0, 2)];
        _crossOutLine.backgroundColor = [UIColor colorWithWhite:191./255. alpha:1];
        
        CGFloat yOffset = 39;
        _categoryImageView = [[UIImageView alloc] initWithFrame:CGRectMake(xOffset, yOffset, 10, 10)];
        
        UIView* tapButton = [Util tapViewWithFrame:_checkView.frame target:self selector:@selector(iconClicked:) andMessage:nil];
        _subtitleView = [[UILabel alloc] initWithFrame:CGRectMake(82, yOffset - 1, 0, 0)];
        _subtitleView.font = [UIFont stampedFontWithSize:12];
        _subtitleView.textColor = [UIColor stampedGrayColor];
        _subtitleView.textAlignment = UITextAlignmentLeft;
        _subtitleView.lineBreakMode = UILineBreakModeTailTruncation;
        
        _stampImage = [[UIImageView alloc] initWithFrame:CGRectMake(0, 0, STStampImageSize18, STStampImageSize18)];
        
        _todoDots = [[UIView alloc] initWithFrame:CGRectMake(xOffset, 59, 235, 1)];
        
        CAShapeLayer *layer = [CAShapeLayer layer];
        layer.contentsScale = [[UIScreen mainScreen] scale];
        layer.fillColor = [UIColor clearColor].CGColor;
        layer.strokeColor = [UIColor colorWithRed:0.8509f green:0.8509f blue:0.8509f alpha:1.0f].CGColor;
        layer.lineDashPattern = [NSArray arrayWithObjects:[NSNumber numberWithFloat:1], [NSNumber numberWithFloat:2], nil];
        layer.frame = CGRectMake(0, 0, _todoDots.frame.size.width, _todoDots.frame.size.height);
        layer.path = [UIBezierPath bezierPathWithRect:layer.bounds].CGPath;
        layer.strokeEnd = .5;
        [_todoDots.layer addSublayer:layer];
        
        _previews = [[STPreviewsView alloc] init];
        [Util reframeView:_previews withDeltas:CGRectMake(xOffset, 66, 0, 0)];
        
        [self.contentView addSubview:_backgroundGradient];
        [self.contentView addSubview:_checkView];
        [self.contentView addSubview:_titleView];
        [self.contentView addSubview:_stampImage];
        [self.contentView addSubview:_crossOutLine];
        [self.contentView addSubview:_categoryImageView];
        [self.contentView addSubview:_subtitleView];
        [self.contentView addSubview:_todoDots];
        [self.contentView addSubview:_previews];
        [self.contentView addSubview:tapButton];
        
    }
    return self;
}   

- (void)dealloc
{
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [_backgroundGradient release];
    [_checkView release];
    [_titleView release];
    [_stampImage release];
    [_crossOutLine release];
    [_categoryImageView release];
    [_subtitleView release];
    [_todoDots release];
    [_previews release];
    [_todo release];
    [super dealloc];
}

- (void)iconClicked:(id)notImportant {
    [self.delegate clickedImageForTodo:self.todo];
}

- (void)setupWithTodo:(id<STTodo>)todo {
    _hasPreviews = NO;
    id<STEntity> entity = todo.source.entity;
    _titleView.text = entity.title;
    _titleView.textColor = [UIColor stampedBlackColor];
    [_titleView sizeToFit];
    if (_titleView.frame.size.width > 225) {
        CGRect frame = _titleView.frame;
        frame.size.width = 225;
        _titleView.frame = frame;
    }
    _stampImage.frame = CGRectMake(CGRectGetMaxX(_titleView.frame)- 5, 
                                   _titleView.frame.origin.y - 5,
                                   _stampImage.frame.size.width,
                                   _stampImage.frame.size.height);
    
    _crossOutLine.frame = CGRectMake(_titleView.frame.origin.x,
                                     _titleView.frame.origin.y + 12,
                                     _titleView.frame.size.width,
                                     2);
    
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
    _stampImage.hidden = YES;
    _crossOutLine.hidden = YES;
    _todoDots.hidden = YES;
    _backgroundGradient.hidden = YES;
    _previews.hidden = YES;
    _stampImage.image = nil;
    if (state == STTodoStateStamped) {
        imageName = @"TEMP_todo_done";
        _stampImage.hidden = NO;
        _stampImage.image = [Util stampImageForUser:[STStampedAPI sharedInstance].currentUser withSize:STStampImageSize18];
    }
    else if (state == STTodoStateDone) {
        imageName = @"todo_markedasdone";
        _crossOutLine.hidden = NO;
        _titleView.textColor = [UIColor colorWithWhite:191./255. alpha:1];
    }
    else {
        imageName = @"TEMP_todo_not_done";
    }
    _checkView.image = [UIImage imageNamed:imageName];
    
    STSimplePreviews* previews = [[[STSimplePreviews alloc] init] autorelease];
    previews.todos = todo.previews.todos;
    if (previews.todos.count) {
        _hasPreviews = YES;
        _backgroundGradient.hidden = NO;
        _todoDots.hidden = NO;
        _previews.hidden = NO;
        [_previews setupWithPreview:previews maxRows:1];
    }
    
    self.todo = todo;
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    if (selected) {
        _backgroundGradient.hidden = YES;
    }
    else {
        _backgroundGradient.hidden = !self.hasPreviews;
    }
    [super setSelected:selected animated:animated];
}

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
    if (highlighted) {
        _backgroundGradient.hidden = YES;
    }
    else {
        _backgroundGradient.hidden = !self.hasPreviews;
    }    
    [super setHighlighted:highlighted animated:animated];
    _crossOutLine.backgroundColor = [UIColor colorWithWhite:191./255. alpha:1];
}

@end

@implementation STTodoViewController

@synthesize cache = _cache;
@synthesize snapshot = _snapshot;
@synthesize reloading = _reloading;
@synthesize dirty = _dirty;
@synthesize actionSheetTodo = _actionSheetTodo;
@synthesize cancellations = _cancellations;

- (id)init
{
    self = [super init];
    if (self) {
        _cancellations = [[NSMutableArray alloc] init];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheUpdate:) name:STCacheDidChangeNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheWillLoadPage:) name:STCacheWillLoadPageNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheDidLoadPage:) name:STCacheDidLoadPageNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(applicationDidBecomeActive:) name:UIApplicationDidBecomeActiveNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(localTodoModification:) name:STStampedAPILocalTodoModificationNotification object:nil];
        _cache = [[STSharedCaches cacheForTodos] retain];
        if (_cache) {
            _snapshot = [[_cache snapshot] retain];
        }
        else {
            [STSharedCaches cacheForTodosWithCallback:^(STCache *cache, NSError *error, STCancellation *cancellation) {
                _cache = [cache retain];
                _snapshot = [[_cache snapshot] retain];
            }];
        }
    }
    return self;
}

- (void)localTodoModification:(id)notImportant {
    self.dirty = YES;
}

- (void)dealloc
{
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [_cache release];
    [_snapshot release];
    [_actionSheetTodo release];
    [self cancelPendingOps];
    [_cancellations release];
    [super dealloc];
}

- (void)cancelPendingOps {
    for (STCancellation* cancellation in self.cancellations) {
        [cancellation cancel];
    }
    [self.cancellations removeAllObjects];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    self.tableView.separatorColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
    
    [Util addHomeButtonToController:self withBadge:YES];
    [Util addCreateStampButtonToController:self];
    
    self.dirty = YES;
}

- (void)viewDidUnload
{
    [super viewDidUnload];
}

- (void)viewDidAppear:(BOOL)animated {
    if (self.dirty) {
        [self reloadDataSource];
    }
    self.dirty = NO;
    [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];
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
    return self.snapshot.count;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 1;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    id<STTodo> todo = [self.snapshot objectAtIndex:indexPath.row];
    if (todo.previews.todos.count) {
        return 107;
    }
    return 64;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    id<STTodo> todo = [self.snapshot objectAtIndex:indexPath.row];
    STTodoCell* cell = [tableView dequeueReusableCellWithIdentifier:_todoReuseIdentifier];
    if (!cell) {
        cell = [[[STTodoCell alloc] init] autorelease];
    }
    [cell setupWithTodo:todo];
    cell.delegate = self;
    return cell;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
    id<STTodo> todo = [self.snapshot objectAtIndex:indexPath.row];
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewEntity:todo.source.entity.entityID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

#pragma mark - Cache Methods

- (void)reloadTableView:(BOOL)preserveOffset {
    if (preserveOffset) {
        CGPoint offset = self.tableView.contentOffset;
        [self.tableView reloadData];
        self.tableView.contentOffset = offset;
        
    } else {
        [self.tableView reloadData];
    }
}

- (void)cacheWillLoadPage:(NSNotification *)notification {
    self.reloading = YES;
    //[self.tableView reloadData];
}

- (void)cacheDidLoadPage:(NSNotification *)notification {
    self.reloading = NO;
    [self dataSourceDidFinishLoading];
    //[self.tableView reloadData];
}

- (void)cacheUpdate:(NSNotification *)notification {
    if (self.cache) {
        self.snapshot = self.cache.snapshot;
        [self reloadTableView:YES];
    }
}

#pragma mark - STRestController 

- (BOOL)dataSourceReloading {
    return self.reloading;
}

- (void)loadNextPage {
    NSLog(@"loadNextPage");
    [self.cache refreshAtIndex:self.snapshot.count force:NO];
}

- (BOOL)dataSourceHasMoreData {
    return self.cache.hasMore;
}

- (void)reloadDataSource {
    NSLog(@"reloading");
    if (self.dirty) {
        [self.cache updateAllWithAccellerator:[STStampedAPI sharedInstance]];
    }
    self.dirty = NO;
    [self.cache refreshAtIndex:-1 force:YES];
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return self.snapshot.count == 0;
}

- (void)setupNoDataView:(NoDataView*)view {
    view.custom = YES;
    
    UIView* waterMark = [NoDataUtil waterMarkWithImage:[UIImage imageNamed:@"watermark_no_todos"]
                                                 title:@"No to-do's" 
                                                  body:@"To add a to-do, just tap this guy when you see it."
                                               options:nil];
//    
//    UIImageView* waterMark = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"watermark_no_todos"]] autorelease];
//    UILabel* top = [Util viewWithText:@"No to-do's"
//                                 font:[UIFont stampedBoldFontWithSize:12]
//                                color:[UIColor stampedGrayColor]
//                                 mode:UILineBreakModeTailTruncation
//                           andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
//    UILabel* bottom = [Util viewWithText:@"To add a to-do, just tap this guy when you see it."
//                                    font:[UIFont stampedFontWithSize:12]
//                                   color:[UIColor stampedGrayColor]
//                                    mode:UILineBreakModeTailTruncation
//                              andMaxSize:CGSizeMake(135, CGFLOAT_MAX)];
//    top.textAlignment = UITextAlignmentCenter;
//    bottom.textAlignment = UITextAlignmentCenter;
//    CGFloat adjustment = 84;
//    top.frame = [Util centeredAndBounded:top.frame.size inFrame:waterMark.frame];
//    [Util reframeView:top withDeltas:CGRectMake(0, -14 - adjustment, 0, 0)];
//    bottom.frame = [Util centeredAndBounded:bottom.frame.size inFrame:waterMark.frame];
//    [Util reframeView:bottom withDeltas:CGRectMake(0, 9 - adjustment, 0, 0)];
//    [waterMark addSubview:top];
//    [waterMark addSubview:bottom];
    waterMark.frame = [Util centeredAndBounded:waterMark.frame.size inFrame:CGRectMake(0, 0, view.frame.size.width, view.frame.size.height)];
    [view addSubview:waterMark];
}

- (void)applicationDidBecomeActive:(id)notImportant {
    [self reloadDataSource];
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
                                                                                          STObjectSetAccelerator* accel = [STObjectSetAccelerator acceleratorForObjects:[NSArray arrayWithObject:todo]];
                                                                                          [self.cache updateAllWithAccellerator:accel];
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
