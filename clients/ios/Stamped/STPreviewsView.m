//
//  STPreviewsView.m
//  Stamped
//
//  Created by Landon Judkins on 4/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STPreviewsView.h"
#import "Util.h"
#import "STActionManager.h"
#import "STStampedActions.h"
#import <QuartzCore/QuartzCore.h>
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STButton.h"
#import "STActionPair.h"
#import "ImageLoader.h"
#import "UserStampView.h"
#import "STUsersViewController.h"
#import "STImageCache.h"

#define kPreviewCellWidth 33.0f
#define kPreviewCellHeight 33.0f

@interface STPreviewView : UIControl {
    UIImageView *_imageView;
    UIView *highlightView;
    UserStampView *_stampView;
}
@property (nonatomic, retain) UIImageView *iconImageView;
@property (nonatomic, retain) NSURL *imageURL;
@property (nonatomic, readwrite, retain) STActionPair* pair;

- (void)setupImageWithUser:(id<STUser>)user;
- (void)setupWithUser:(id<STUser>)user;
@end


@interface STPreviewsView ()
@property (nonatomic, readonly, retain) NSMutableArray *views;
@property (nonatomic, readwrite, retain) id<STPreviews> previews;
@end

@implementation STPreviewsView

@synthesize views = _views;
@synthesize previews = _previews;

static const CGFloat _cellWidth = 35;
static const CGFloat _cellHeight = 35;
static const NSInteger _cellsPerRow = 7;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        _views = [[NSMutableArray alloc] init];
        
        // alloc initial preview views
        for (NSInteger i = 0; i < 7; i++) {
            STPreviewView *view = [[STPreviewView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, kPreviewCellWidth, kPreviewCellHeight)];
            [_views addObject:view];
            [view release];
        }
        
    }
    return self;
}

- (void)dealloc {
    [_views release], _views=nil;
    [_previews release];
    [super dealloc];
}

#pragma mark - Reuse

- (STPreviewView*)dequeuePreviewViewAtIndex:(NSInteger)index {
    
    if (index < [self.views count]) {
        STPreviewView *view = [self.views objectAtIndex:index];
        view.pair = nil;
        return view;
    }
    
    STPreviewView *view = [[STPreviewView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, kPreviewCellWidth, kPreviewCellHeight)];
    [_views addObject:view];
    return [view autorelease];
    
}


#pragma mark - Setup

- (void)setupWithPreview:(id<STPreviews>)previews maxRows:(NSInteger)maxRows {
    self.previews = previews;
    [self.subviews makeObjectsPerformSelector:@selector(removeFromSuperview)];
    
    NSInteger index = 0;
    NSInteger total = [STPreviewsView totalItemsForPreviews:previews];
    if (total > 0) {
        
        NSInteger numberOfRows = [STPreviewsView totalRowsForPreviews:previews andMaxRows:maxRows];
        self.frame = CGRectMake(self.frame.origin.x, self.frame.origin.y, floorf(_cellWidth * MIN(_cellsPerRow, total)), floorf(numberOfRows * _cellHeight));
        NSInteger limit = MIN(_cellsPerRow * numberOfRows, total);
        BOOL continuedFlag = (limit < total);
        
        for (id<STStampPreview> credit in previews.credits) {
            if (index >= limit) break;
            
            STActionContext *context = [STActionContext context];
            id<STAction> action = [STStampedActions actionViewStamp:credit.stampID withOutputContext:context];
            STPreviewView *view = [self dequeuePreviewViewAtIndex:index];
            [view setupImageWithUser:credit.user];
            //            view.imageURL = [NSURL URLWithString:[Util profileImageURLForUser:credit.user withSize:size]];
            [view setupWithUser:credit.user];
            view.pair = [STActionPair actionPairWithAction:action andContext:context];
            index++;
            
        }
        for (id<STStampPreview> preview in previews.stamps) {
            id<STUser> user = preview.user;
            if (index >= limit) break;
            
            STActionContext *context = [STActionContext context];
            context.user = user;
            id<STAction> action = [STStampedActions actionViewStamp:preview.stampID withOutputContext:context];
            STPreviewView *view = [self dequeuePreviewViewAtIndex:index];
            [view setupImageWithUser:user];
            //            view.imageURL = [NSURL URLWithString:[Util profileImageURLForUser:user withSize:size]];
            [view setupWithUser:user];
            view.pair = [STActionPair actionPairWithAction:action andContext:context];
            index++;
            
        }
        
        UIImage *likeIcon = [UIImage imageNamed:@"like_mini"];
        for (id<STUser> like in previews.likes) {
            if (index >= limit) break;
            
            STActionContext *context = [STActionContext context];
            context.user = like;
            id<STAction> action = [STStampedActions actionViewUser:like.userID withOutputContext:context];
            STPreviewView *view = [self dequeuePreviewViewAtIndex:index];
            [view setupImageWithUser:like];
            //            view.imageURL = [NSURL URLWithString:[Util profileImageURLForUser:like withSize:size]];
            view.iconImageView.image = likeIcon;
            [view setupWithUser:nil];
            view.pair = [STActionPair actionPairWithAction:action andContext:context];
            index++;
            
        }
        
        UIImage *todoIcon = [UIImage imageNamed:@"todo_mini"];
        for (id<STUser> todo in previews.todos) {
            if (index >= limit)   break;
            
            STActionContext *context = [STActionContext context];
            context.user = todo;
            id<STAction> action = [STStampedActions actionViewUser:todo.userID withOutputContext:context];
            STPreviewView *view = [self dequeuePreviewViewAtIndex:index];
            [view setupImageWithUser:todo];
            //            view.imageURL = [NSURL URLWithString:[Util profileImageURLForUser:todo withSize:size]];
            view.iconImageView.image = todoIcon;
            [view setupWithUser:nil];
            view.pair = [STActionPair actionPairWithAction:action andContext:context];
            index++;
            
        }
        
        for (NSInteger i = 0; i < limit; i++) {
            
            NSInteger col = i % _cellsPerRow;
            NSInteger row = i / _cellsPerRow;
            CGFloat xOffset = col * _cellWidth;
            CGFloat yOffset = row * _cellHeight;
            
            if (i == limit - 1 && continuedFlag) {
                
                UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
                [button setImage:[UIImage imageNamed:@"previews_more_icon.png"] forState:UIControlStateNormal];
                [button addTarget:self action:@selector(seeAllClicked:) forControlEvents:UIControlEventTouchUpInside];
                button.frame = CGRectMake(xOffset, yOffset, 33, 33);
                [self addSubview:button];
                
            } else {
                
                STPreviewView *view = [_views objectAtIndex:i];
                view.frame = CGRectMake(xOffset, yOffset-1.0f, kPreviewCellWidth, kPreviewCellHeight);
                if (!view.superview) {
                    [self addSubview:view];
                }
                
            }
        }
        
    }
    
    
}

- (void)seeAllClicked:(id)notImportant {
    NSMutableArray* userIDs = [NSMutableArray array];
    NSMutableDictionary* stamps = [NSMutableDictionary dictionary];
    if (self.previews.credits.count) {
        for (id<STStampPreview> credit in self.previews.credits) {
            [userIDs addObject:credit.user.userID];
        }
    }
    if (self.previews.stamps.count) {
        for (id<STStampPreview> stamp in self.previews.stamps) {
            [userIDs addObject:stamp.user.userID];
            [stamps setObject:stamp.stampID forKey:stamp.user.userID];
        }
    }
    if (self.previews.likes.count) {
        for (id<STUser> user in self.previews.likes) {
            [userIDs addObject:user.userID];
        }
    }
    if (self.previews.todos.count) {
        for (id<STUser> user in self.previews.todos) {
            [userIDs addObject:user.userID];
        }
    }
    STUsersViewController* controller = [[[STUsersViewController alloc] initWithUserIDs:userIDs] autorelease];
    controller.userIDToStampID = stamps;
    [Util pushController:controller modal:NO animated:YES];
}

- (void)setupWithStamp:(id<STStamp>)stamp maxRows:(NSInteger)maxRows {
    [self setupWithPreview:stamp.previews maxRows:maxRows];
}


#pragma mark Class Methods

+ (NSInteger)totalItemsForPreviews:(id<STPreviews>)previews {
    if (previews) {
        return previews.credits.count + previews.likes.count + previews.todos.count + previews.stamps.count;
    }
    return 0;
}

+ (NSInteger)totalRowsForPreviews:(id<STPreviews>)previews andMaxRows:(NSInteger)maxRows {
    NSInteger itemsCount = [STPreviewsView totalItemsForPreviews:previews];
    NSInteger rows = itemsCount / _cellsPerRow;
    rows += itemsCount % _cellsPerRow ? 1 : 0;
    return MIN(maxRows,rows);
}

+ (CGFloat)previewHeightForStamp:(id<STStamp>)stamp andMaxRows:(NSInteger)maxRows {
    return [STPreviewsView previewHeightForPreviews:stamp.previews andMaxRows:maxRows];
}

+ (CGFloat)previewHeightForPreviews:(id<STPreviews>)previews andMaxRows:(NSInteger)maxRows {
    return [STPreviewsView totalRowsForPreviews:previews andMaxRows:maxRows] * _cellHeight;
}

+ (NSArray*)imagesForPreviewWithStamp:(id<STStamp>)stamp andMaxRows:(NSInteger)maxRows {
    return [STPreviewsView imagesForPreviewWithPreviews:stamp.previews andMaxRows:maxRows];
}

+ (NSArray*)imagesForPreviewWithPreviews:(id<STPreviews>)previews andMaxRows:(NSInteger)maxRows {
    NSMutableArray* images = [NSMutableArray array];
    NSInteger total = [STPreviewsView totalItemsForPreviews:previews];
    if (total > 0) {
        NSInteger numberOfRows = [STPreviewsView totalRowsForPreviews:previews andMaxRows:maxRows];
        NSInteger limit = MIN(_cellsPerRow * numberOfRows, total);
        //BOOL continuedFlag = NO;
        if (limit < total) {
            // TODO add support for continued button
            //continuedFlag = YES;
        }
        
        STProfileImageSize size = STProfileImageSize48;
        for (id<STStampPreview> credit in previews.credits) {
            if (images.count < limit) {
                [images addObject:[Util profileImageURLForUser:credit.user withSize:size]];
            }
            else {
                break;
            }
        }
        for (id<STStampPreview> preview in previews.stamps) {
            id<STUser> user = preview.user;
            if (images.count < limit) {
                [images addObject:[Util profileImageURLForUser:user withSize:size]];
            }
            else {
                break;
            }
        }
        for (id<STUser> like in previews.likes) {
            if (images.count < limit) {
                [images addObject:[Util profileImageURLForUser:like withSize:size]];
            }
            else {
                break;
            }
        }
        for (id<STUser> todo in previews.todos) {
            if (images.count < limit) {
                [images addObject:[Util profileImageURLForUser:todo withSize:size]];
            }
            else {
                break;
            }
        }
    }
    return images;
}

@end


#pragma mark - STPreviewView

@implementation STPreviewView
@synthesize pair = _pair;
@synthesize imageURL=_imageURL;
@synthesize iconImageView = _iconImageView;

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        UIView *background = [[UIView alloc] initWithFrame:CGRectInset(self.bounds, 2.0f, 2.0f)];
        background.userInteractionEnabled = NO;
        background.backgroundColor = [UIColor whiteColor];
        background.layer.shadowPath = [UIBezierPath bezierPathWithRect:background.bounds].CGPath;
        background.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
        background.layer.shadowRadius = 1.0f;
        background.layer.shadowOpacity = 0.2f;
        background.layer.rasterizationScale = [[UIScreen mainScreen] scale];
        background.layer.shouldRasterize = YES;
        [self addSubview:background];
        [background release];
        
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectInset(self.bounds, 3.0f, 3.0f)];
        imageView.backgroundColor = [UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [self addSubview:imageView];
        _imageView = imageView;
        [imageView release];
        
        imageView = [[UIImageView alloc] initWithFrame:CGRectMake(self.bounds.size.width - 14.0f, self.bounds.size.height- 14.0f, 16.0f, 16.0f)];
        imageView.contentMode = UIViewContentModeCenter;
        imageView.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleLeftMargin;
        [self addSubview:imageView];
        self.iconImageView = imageView;
        [imageView release];
        
        UserStampView *stampView = [[UserStampView alloc] initWithFrame:CGRectInset(self.iconImageView.frame, 2, 2)];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleLeftMargin;
        stampView.size = STStampImageSize12;
        stampView.userInteractionEnabled = NO;
        stampView.hidden = YES;
        [self addSubview:stampView];
        _stampView = stampView;
        [stampView release];
        
        [self addTarget:self action:@selector(clicked:) forControlEvents:UIControlEventTouchUpInside];
        
    }
    return self;
    
}

- (void)dealloc {
    _stampView=nil;
    _imageView=nil;
    self.iconImageView = nil;
    [_pair release];
    [super dealloc];
}

- (void)clicked:(id)notImportant {
    if (self.pair) {
        [self.pair executeAction];
    }
}

#pragma mark - Setters

- (void)setupWithUser:(id<STUser>)user {
    
    if (user) {
        
        _stampView.hidden = NO;
        [_stampView setupWithUser:user];
        self.iconImageView.hidden = YES;
        self.iconImageView.image = nil;
        
    } else {
        
        _stampView.hidden = YES;
        self.iconImageView.hidden = NO;
        
    }
    
}

- (void)setImageURL:(NSURL *)imageURL {
    if (_imageURL && [_imageURL isEqual:imageURL]) return;
    [_imageURL release], _imageURL=nil;
    _imageURL = [imageURL retain];
    
    _imageView.image = nil;
    if (imageURL) {
        [[STImageCache sharedInstance] imageForImageURL:imageURL.absoluteString andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
            UIGraphicsBeginImageContextWithOptions(self.bounds.size, YES, 0);
            [image drawInRect:CGRectMake(0.0f, 0.0f, self.bounds.size.width, self.bounds.size.height)];
            UIImage *scaledImage = UIGraphicsGetImageFromCurrentImageContext();
            UIGraphicsEndImageContext();
            if ([_imageURL isEqual:imageURL]) {
                _imageView.image = scaledImage;
            }
        }];
    }
    
    //    [[ImageLoader sharedLoader] imageForURL:_imageURL style:^UIImage*(UIImage *image) {
    //
    //        UIGraphicsBeginImageContextWithOptions(self.bounds.size, YES, 0);
    //        [image drawInRect:CGRectMake(0.0f, 0.0f, self.bounds.size.width, self.bounds.size.height)];
    //        UIImage *scaledImage = UIGraphicsGetImageFromCurrentImageContext();
    //        UIGraphicsEndImageContext();
    //        return scaledImage;
    //        
    //    } styleIdentifier:@"st_preview@2x.jpg" completion:^(UIImage *image, NSURL *url) {
    //        if ([_imageURL isEqual:url]) {
    //            _imageView.image = image;
    //        }
    //    }];
    
}

- (void)adjustHighlight:(BOOL)highlighted {
    
    if (_stampView) {
        [_stampView setHighlighted:highlighted];
    }
    
    if (highlighted) {
        
        if (!highlightView) {
            UIView *view = [[UIView alloc] initWithFrame:_imageView.frame];
            view.backgroundColor = [UIColor blackColor];
            view.layer.cornerRadius = 2.0f;
            view.layer.masksToBounds = YES;
            [view setAlpha: 0.5];
            [self addSubview:view];
            [view release];
            highlightView = view;
        }
        
    } else {
        
        if (highlightView) {
            __block UIView *view = highlightView;
            highlightView = nil;
            BOOL _enabled = [UIView areAnimationsEnabled];
            [UIView setAnimationsEnabled:YES];
            [UIView animateWithDuration:0.25f animations:^{
                view.alpha = 0.0f;
            } completion:^(BOOL finished) {
                [view removeFromSuperview];
            }];
            [UIView setAnimationsEnabled:_enabled];
            
        }
        
    }
    
}

- (void)setupImageWithUser:(id<STUser>)user {
    STProfileImageSize size = STProfileImageSize48;
    BOOL usedCurrentUserImage = NO;
    self.imageURL = nil;
    if ([user.userID isEqualToString:[STStampedAPI sharedInstance].currentUser.userID]) {
        UIImage* userImage = [STStampedAPI sharedInstance].currentUserImage;
        if (userImage) {
            _imageView.image = userImage;
            usedCurrentUserImage = YES;
        }
    }
    if (!usedCurrentUserImage) {
        self.imageURL = [NSURL URLWithString:[Util profileImageURLForUser:user withSize:size]];
    }
}

- (void)setHighlighted:(BOOL)highlighted {
    [super setHighlighted:highlighted];
    [self adjustHighlight:highlighted];
}

- (void)setSelected:(BOOL)selected {
    [super setSelected:selected];
    [self adjustHighlight:selected];
}

@end
