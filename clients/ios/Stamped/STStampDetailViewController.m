//
//  STStampDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailViewController.h"

#import <Twitter/Twitter.h>

#import "EntityDetailViewController.h"
#import "Util.h"
#import "STSynchronousWrapper.h"
#import "STScrollViewContainer.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STStampDetailHeaderView.h"
#import "STActionManager.h"
#import "STStampedActions.h"
#import "STStampedAPI.h"
#import "STStampDetailCommentsView.h"
#import "STToolbarView.h"
#import "STLikeButton.h"
#import "STTodoButton.h"
#import "STStampButton.h"
#import "STStampedAPI.h"
#import "STButton.h"
#import "TTTAttributedLabel.h"
#import "STCommentButton.h"
#import "STShareButton.h"
#import "STCreateCommentView.h"
#import "STHoverToolbar.h"
#import "STNavigationItem.h"
#import "STRootViewController.h"

typedef enum {
    CommentPanDirectionUp = 0,
    CommentPanDirectionDown,
} CommentPanDirection;

@interface STStampDetailToolbar : UIView

- (id)initWithParent:(UIView*)view controller:(STStampDetailViewController*)controller andStamp:(id<STStamp>)stamp;
- (void)toggleToolbar:(id)button;

@property (nonatomic, readonly, retain) NSArray* buttons;
@property (nonatomic, readwrite, assign) BOOL expanded;
@property (nonatomic, readonly, retain) UIView* expandButton;
@property (nonatomic, readonly, retain) UIView* buttonContainer;

@end

@interface STStampDetailViewController () <UIActionSheetDelegate, UITextViewDelegate>

@property (nonatomic, readwrite, retain) id<STStamp> stamp;

- (void)showCommentView:(BOOL)animated;
- (void)_didLoadEntityDetail:(id<STEntityDetail>)detail;
- (void)_deleteStampButtonPressed:(id)caller;
- (void)commentButtonPressed;

@property (nonatomic, readonly, retain) STStampDetailHeaderView* headerView;
@property (nonatomic, readonly, retain) STStampDetailCommentsView* commentsView;
@property (nonatomic, readwrite, retain) STCancellation* entityDetailCancellation;
@property (nonatomic, readwrite, retain) STCancellation* stampCancellation;
@property (nonatomic, readonly, retain) STCreateCommentView *commentView;
@property (nonatomic, readonly, retain) UIPanGestureRecognizer *panGesture;
@property (nonatomic, assign) CommentPanDirection direction;
@property (nonatomic, assign) CGRect beginFrame;
@property (nonatomic, assign) CGRect commentBeginFrame;
@property (nonatomic, readwrite, retain) UIView* entityDetailView;

@end

@implementation STStampDetailToolbar

@synthesize buttons = buttons_;
@synthesize expanded = expanded_;
@synthesize expandButton = expandButton_;
@synthesize buttonContainer = buttonContainer_;

- (id)initWithParent:(UIView*)view controller:(STStampDetailViewController*)controller andStamp:(id<STStamp>)stamp {
    
    UIImage *image = [UIImage imageNamed:@"st_detail_action_bg"];
    
    CGFloat xPadding = 5;
    CGFloat yPadding = 10;
    CGFloat height = image.size.height;
    CGRect frame = CGRectMake(xPadding, view.frame.size.height - (height + yPadding), view.frame.size.width - (2 * xPadding), height);
    
    if ((self = [super initWithFrame:frame])) {
        expanded_ = YES;
        
        UIImageView *background = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        [self addSubview:background];
        CGRect frame = background.frame;
        frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
        frame.size.width = self.bounds.size.width;
        background.frame = frame;
        [background release];
        
        UIImageView* imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"sDetailBar_btn_more"]] autorelease];
        UIImageView* imageView2 = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"sDetailBar_btn_more_active"]] autorelease];
        expandButton_ = [[STButton alloc] initWithFrame:imageView.frame 
                                             normalView:imageView 
                                             activeView:imageView2 
                                                 target:self 
                                              andAction:@selector(toggleToolbar:)];
        [Util reframeView:expandButton_ withDeltas:CGRectMake(frame.size.width - (expandButton_.frame.size.width + 20), 10, 15, 0)];
        expandButton_.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin;
        
        __block STStampDetailViewController* weakController = controller;
        STCommentButton* commentButton = [[[STCommentButton alloc] initWithCallback:^{
            [weakController commentButtonPressed];
        }] autorelease];
        
        buttons_ = [[NSMutableArray arrayWithObjects:
                     [[[STLikeButton alloc] initWithStamp:stamp] autorelease],
                     commentButton,
                     [[[STStampButton alloc] initWithStamp:stamp] autorelease],
                     [[[STTodoButton alloc] initWithStamp:stamp] autorelease],
                     [[[STShareButton alloc] initWithCallback:^{
            [Util executeOnMainThread:^{
                [Util warnWithMessage:@"☝ No leaking Stamped 2.0!" andBlock:nil];
            }];
        }] autorelease], nil] retain];
        
        CGFloat buttonSpacing = 60;
        buttonContainer_ = [[UIView alloc] initWithFrame:CGRectMake(0, -3, CGRectGetMinX(expandButton_.frame)+50, frame.size.height-7)];
        buttonContainer_.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        for (NSInteger i = 0; i < buttons_.count; i++) {
            UIView* button = [buttons_ objectAtIndex:i];
            [Util reframeView:button withDeltas:CGRectMake(-5 + (i * buttonSpacing), -4, 0, 0)];
            [buttonContainer_ addSubview:button];
        }
        buttonContainer_.clipsToBounds = NO;
        [self addSubview:buttonContainer_];
        self.clipsToBounds = YES;
        [Util reframeView:expandButton_ withDeltas:CGRectMake(3, -3, 0, 0)];
        [self addSubview:expandButton_];
        
        BOOL _enabled = [UIView areAnimationsEnabled];
        [UIView setAnimationsEnabled:NO];
        [self toggleToolbar:nil];
        [UIView setAnimationsEnabled:_enabled];
        
    }
    return self;
}

- (void)toggleToolbar:(id)notImportant {
    
    CGFloat delta = 190.0f;
    
    CGRect frame = self.frame;
    CGFloat width = [[UIScreen mainScreen] applicationFrame].size.width;
    frame.size.width = self.expanded ? delta : width - 10.0f;
    frame.origin.x = self.expanded ?  width - (delta+5.0f) : 5.0f;
    [UIView animateWithDuration:0.25f animations:^{
        self.frame = frame;
    }];
    
    [UIView animateWithDuration:self.expanded ? 0.1f : 0.15f delay:self.expanded ? 0.0f : 0.1f options:UIViewAnimationCurveEaseInOut animations:^{
        
        CGFloat originX = 4.0f;
        
        for (NSInteger i = 0; i < buttons_.count; i++) {
            
            UIView *button = [buttons_ objectAtIndex:i];
            CGRect buttonFrame = button.frame;
            buttonFrame.origin.x = originX;
            originX += self.expanded ? 46.0f : 52.0f;
            button.frame = buttonFrame;
            
            if (self.expanded && CGRectGetMaxX(buttonFrame) - 20 > frame.size.width - 50) {
                button.alpha = 0;
            } else {
                button.alpha = 1;
            }
            
        }
        
    } completion:^(BOOL finished){}];
    
    self.expanded = !self.expanded;
    
}

- (void)reloadStampedData {
    for (id view in self.buttonContainer.subviews) {
        if ([view respondsToSelector:@selector(reloadStampedData)]) {
            [view reloadStampedData]; 
        }
    }
}

@end

@implementation STStampDetailViewController

@synthesize headerView = _headerView;
@synthesize commentsView = _commentsView;
@synthesize stamp = _stamp;
@synthesize toolbar = _toolbar;
@synthesize entityDetailCancellation = entityDetailCancellation_;
@synthesize stampCancellation = _stampCancellation;
@synthesize commentView = _commentView;
@synthesize panGesture=_panGesture;
@synthesize direction;
@synthesize beginFrame;
@synthesize commentBeginFrame;
@synthesize entityDetailView = _entityDetailView;

- (id)initWithStamp:(id<STStamp>)stamp {
    id<STStamp> cachedStamp = [[STStampedAPI sharedInstance] cachedStampForStampID:stamp.stampID];
    if (cachedStamp) {
        stamp = cachedStamp;
    }
    self = [super init];
    if (self) {
        _stamp = [stamp retain];
    }
    return self;
}

- (void)dealloc {
    
    [_headerView release];
    [_commentsView release];
    [_stamp release];
    [_toolbar release];
    [entityDetailCancellation_ cancel];
    [entityDetailCancellation_ release];
    [_entityDetailView release];
    [_commentView release], _commentView=nil;
    [_panGesture release], _panGesture=nil;
    [super dealloc];
}


#pragma mark - View cycle

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!_headerView) {
        _headerView = [[STStampDetailHeaderView alloc] initWithStamp:self.stamp];
        [self.scrollView appendChildView:_headerView];
    }
    
    if (!_commentsView) {
        _commentsView = [[STStampDetailCommentsView alloc] initWithStamp:self.stamp andDelegate:self.scrollView];
        [self.scrollView appendChildView:_commentsView];
    }
    
    if ([STStampedAPI.sharedInstance.currentUser.userID isEqualToString:self.stamp.user.userID]) {
        STNavigationItem* rightButton = [[[STNavigationItem alloc] initWithTitle:@"Delete" style:UIBarButtonItemStylePlain target:self action:@selector(_deleteStampButtonPressed:)] autorelease];
        self.navigationItem.rightBarButtonItem = rightButton;
    }
    
    //UIView* newToolbar = [[[STStampDetailToolbar alloc] initWithParent:self.view controller:self andStamp:self.stamp] autorelease];
    //[self.view addSubview:newToolbar];
    if (LOGGED_IN) {
        STHoverToolbar* toolbar = [[[STHoverToolbar alloc] initWithStamp:self.stamp] autorelease];
        toolbar.target = self;
        toolbar.commentAction = @selector(commentButtonPressed);
        toolbar.shareAction = @selector(shareButtonPressed);
        [self.view addSubview:toolbar];
        [toolbar positionInParent];
    }
    
    if (!_panGesture) {
        UIPanGestureRecognizer *pan = [[UIPanGestureRecognizer alloc] initWithTarget:self action:@selector(pan:)];
        pan.delegate = (id<UIGestureRecognizerDelegate>)self;
        [self.scrollView addGestureRecognizer:pan];
        _panGesture = [pan retain];
        [pan setEnabled:NO];
        [pan release];
    }
    
    if (!_commentView) {
        STCreateCommentView *view = [[STCreateCommentView alloc] initWithFrame:CGRectMake(0.0f, self.view.bounds.size.height+44.0f, self.view.bounds.size.width, 44)];
        view.delegate = (id<STCreateCommentViewDelegate>)self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin;
        [self.view addSubview:view];
        _commentView = [view retain];
        [view release];        
    }

}

- (void)loadEntityDetail {
    if (!self.entityDetailCancellation) {
        self.entityDetailCancellation = [[STStampedAPI sharedInstance] entityDetailForEntityID:self.stamp.entity.entityID andCallback:^(id<STEntityDetail> detail, NSError *error, STCancellation *cancellation) {
            self.entityDetailCancellation = nil;
            STSynchronousWrapper* wrapper = [STSynchronousWrapper wrapperForStampDetail:detail withFrame:CGRectMake(0, 0, 320, 200) stamp:self.stamp delegate:self.scrollView];
            [self.scrollView appendChildView:wrapper];
            self.scrollView.contentSize = CGSizeMake(self.scrollView.contentSize.width, self.scrollView.contentSize.height);
            self.entityDetailView = wrapper;
        }];
    }
}

- (void)shareButtonPressed {
    [Util warnWithMessage:@"☝ No leaking Stamped 2.0!" andBlock:nil];
}

- (void)viewDidUnload {
    [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    //[self setUpToolbar];
    [_headerView setNeedsDisplay];
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    [[STActionManager sharedActionManager] setStampContext:self.stamp];
    
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillShow:) name:UIKeyboardWillShowNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillHide:) name:UIKeyboardWillHideNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(localModification:) name:STStampedAPILocalStampModificationNotification object:nil];
    if (!self.entityDetailView) {
        [self loadEntityDetail];
    }
}

- (void)viewWillDisappear:(BOOL)animated {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [[STActionManager sharedActionManager] setStampContext:nil];
    [super viewWillDisappear:animated];
}


#pragma mark - STCreateCommentViewDelegate

- (void)cancelComment:(id)sender {
    
    [self.commentView killKeyboard];
    
}

- (void)stCreateCommentView:(STCreateCommentView*)view addedComment:(id<STComment>)comment {
    
    //[self reloadStampedData];
    [view killKeyboard];
    
}

- (void)stCreateCommentViewWillBeginEditing:(STCreateCommentView*)view {
    
    self.title = @"Comment";
    [self.navigationController.navigationBar setNeedsDisplay];
    
    STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(cancelComment:)];
    self.navigationItem.leftBarButtonItem = button;
    [button release];
    
}

- (void)stCreateCommentViewWillEndEditing:(STCreateCommentView*)view {
    
    self.title = nil;
    [self.navigationController.navigationBar setNeedsDisplay];
    
    NSInteger index = [self.navigationController.viewControllers indexOfObject:self];
    if (index!=NSNotFound && index > 0 && [self.navigationController isKindOfClass:[STRootViewController class]]) {
        
        UIViewController *prevController = [self.navigationController.viewControllers objectAtIndex:index-1];
        STNavigationItem *button = [[STNavigationItem alloc] initWithBackButtonTitle:prevController.title style:UIBarButtonItemStyleBordered target:self.navigationController action:@selector(pop:)];
        self.navigationItem.leftBarButtonItem = button;
        [button release];
        
    }
    
}


#pragma mark - Getters

- (UIView *)toolbar {
    return _toolbar;
}


#pragma mark - Stamp Notifications

- (void)localModification:(id)notImportant {
    [self.stampCancellation cancel];
    self.stampCancellation = [[STStampedAPI sharedInstance] stampForStampID:self.stamp.stampID
                                                                forceUpdate:NO
                                                                andCallback:^(id<STStamp> stamp, NSError *error, STCancellation *cancellation) {
                                                                    self.stamp = stamp;
                                                                    [super reloadStampedData];
                                                                }];
}


#pragma mark - Actions

- (void)_deleteStampButtonPressed:(id)caller {
    [Util confirmWithMessage:@"Are you sure?" action:@"Delete" destructive:YES withBlock:^(BOOL confirmed) {
        if (confirmed) {
            STActionContext* context = [STActionContext contextWithCompletionBlock:^(id success, NSError *error) {
                if (!error) {
                    [[Util sharedNavigationController] popViewControllerAnimated:YES];
                }
            }];
            id<STAction> action = [STStampedActions actionDeleteStamp:self.stamp.stampID withOutputContext:context];
            [[STActionManager sharedActionManager] didChooseAction:action withContext:context];    }
    }];
}

- (void)_didLoadEntityDetail:(id<STEntityDetail>)detail {
    CGFloat wrapperHeight = 200;
    CGRect wrapperFrame = CGRectMake(0, 0 , 320, wrapperHeight);
    STSynchronousWrapper* eDetailView = [STSynchronousWrapper wrapperForEntityDetail:detail
                                                                           withFrame:wrapperFrame 
                                                                            andStyle:@"StampDetail" 
                                                                            delegate:self.scrollView];
    [self.scrollView appendChildView:eDetailView];
}

- (void)handleEntityTap:(id)sender {
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewEntity:self.stamp.entity.entityID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)commentButtonPressed {
    
    [self showCommentView:YES];
    
}

- (void)cancelPendingRequests {
    [self.stampCancellation cancel];
    self.stampCancellation = nil;
    [self.entityDetailCancellation cancel];
    self.entityDetailCancellation = nil;
}


#pragma mark - DataSource Loading

- (void)reloadStampedData {
    [self.stampCancellation cancel];
    self.stampCancellation = [[STStampedAPI sharedInstance] stampForStampID:self.stamp.stampID
                                                                forceUpdate:YES 
                                                                andCallback:^(id<STStamp> stamp, NSError *error, STCancellation *cancellation) {
                                                                    self.stamp = stamp;
                                                                    [super reloadStampedData];
                                                                }];
}


#pragma mark - Gestures

- (BOOL)gestureRecognizer:(UIGestureRecognizer *)gestureRecognizer shouldRecognizeSimultaneouslyWithGestureRecognizer:(UIGestureRecognizer *)otherGestureRecognizer {
    return YES;
}

- (void)pan:(UIPanGestureRecognizer*)gesture {
    
    __block CGPoint translation = [gesture translationInView:self.scrollView];
    
    __block UIWindow *window = nil;
    for (UIWindow *aWindow in [[UIApplication sharedApplication] windows]) {
        if ([aWindow isKindOfClass:NSClassFromString(@"UITextEffectsWindow")]) {
            window = aWindow;
            break;
        }
    }
    if (window==nil) {
        return;
    }
    
    if (gesture.state == UIGestureRecognizerStateBegan) {
        beginFrame = window.frame;
        commentBeginFrame = self.commentView.frame;
        direction = CommentPanDirectionUp;
    } 
    
    if (gesture.state == UIGestureRecognizerStateChanged || gesture.state == UIGestureRecognizerStateBegan) {
        
        CGFloat maxOffsetY = (self.view.superview.bounds.size.height - CGRectGetMaxY(commentBeginFrame));
        
        CGFloat prevY = window.frame.origin.y;
        CGRect frame = window.frame;
        CGFloat offsetY = MAX(beginFrame.origin.y, beginFrame.origin.y + translation.y);
        offsetY = MIN(offsetY, beginFrame.origin.y+maxOffsetY);
        frame.origin.y = offsetY;
        window.frame = frame;
        
        if (frame.origin.y != prevY) {
            direction = (frame.origin.y >= prevY) ? CommentPanDirectionDown : CommentPanDirectionUp;
        } 
        
        frame = self.commentView.frame;
        offsetY = MAX(commentBeginFrame.origin.y, commentBeginFrame.origin.y + translation.y);
        offsetY = MIN(offsetY, commentBeginFrame.origin.y+maxOffsetY);
        frame.origin.y = offsetY;
        self.commentView.frame = frame;
        
    } else if (gesture.state == UIGestureRecognizerStateEnded || gesture.state == UIGestureRecognizerStateCancelled) {
        
        // max this animation would move in pts
        CGFloat maxOffsetY = ((self.view.superview.bounds.size.height) - CGRectGetMaxY(commentBeginFrame));
        
        if (direction==CommentPanDirectionUp) {
            
            // calulate animation duration
            CGFloat diff = (window.frame.origin.y - beginFrame.origin.y);
            float duration = (.3/maxOffsetY)*diff;
            
            [UIView animateWithDuration:duration animations:^{
                window.frame = beginFrame;
                self.commentView.frame = commentBeginFrame;
            }];
            
        } else {
            
            CGFloat diff = ((self.view.superview.bounds.size.height) - CGRectGetMaxY(self.commentView.frame)) + 50.0f;
            float duration = (.3/maxOffsetY)*diff;
            
            [UIView animateWithDuration:duration animations:^{
                
                CGRect frame = window.frame;
                frame.origin.y += diff;
                window.frame = frame;
                
                frame = self.commentView.frame;
                frame.origin.y += diff;
                self.commentView.frame = frame;
                self.scrollView.contentInset = UIEdgeInsetsZero;
                
                
            } completion:^(BOOL finished) {
                
                window.frame = beginFrame;
                BOOL _enabled = [UIView areAnimationsEnabled];
                [UIView setAnimationsEnabled:NO];
                [self.commentView killKeyboard];
                [UIView setAnimationsEnabled:_enabled];
                
            }];
            
        }
        
    }
    
}


#pragma mark - Comment View

- (void)showCommentView:(BOOL)animated {
    
    self.commentView.identifier = self.stamp.stampID;
    //_animateKeyboard = animated;
    [self.commentView showAnimated:YES];
    
}


#pragma mark - UIKeyboard Notfications

- (void)keyboardWillShow:(NSNotification*)notification {    
    
    if (self.commentView) {
        [self.commentView keyboardWillShow:[notification userInfo]];
    }
    
    CGRect keyboardFrame = [[[notification userInfo] objectForKey:UIKeyboardFrameEndUserInfoKey] CGRectValue];
    CGFloat contentOffset = self.scrollView.contentOffset.y + keyboardFrame.size.height;
    CGFloat newHeight = (self.scrollView.frame.size.height - keyboardFrame.size.height);
    contentOffset = MIN(contentOffset+40, self.scrollView.contentSize.height - newHeight);
    /*
     BOOL _enabled = [UIView areAnimationsEnabled];
     [UIView setAnimationsEnabled:YES];
     
     [UIView animateWithDuration:0.3 delay:0 options:UIViewAnimationCurveEaseOut animations:^{
     
     self.scrollView.contentInset = UIEdgeInsetsMake(0, 0, keyboardFrame.size.height + 44.0f , 0);
     self.scrollView.scrollIndicatorInsets = self.scrollView.contentInset;
     if (self.scrollView.contentSize.height > newHeight) {
     self.scrollView.contentOffset = CGPointMake(0, contentOffset);
     }
     
     } completion:^(BOOL finished){
     [self.panGesture setEnabled:YES];
     }];
     
     //if (!_animateKeyboard) {
     //    self.scrollView.contentOffset = CGPointZero;
     // }
     [UIView setAnimationsEnabled:_enabled];
     // _animateKeyboard = YES;
     */
    
}

- (void)keyboardWillHide:(NSNotification*)notification {
    
    if (self.commentView) {
        [self.commentView keyboardWillHide:[notification userInfo]];
    }
    /*
     [self.panGesture setEnabled:NO];
     //if (_animateKeyboard) {
     [UIView animateWithDuration:0.3 animations:^{
     self.scrollView.contentInset = UIEdgeInsetsZero;
     self.scrollView.scrollIndicatorInsets = self.scrollView.contentInset;
     }];
     //}
     */
    
}



@end