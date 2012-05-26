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

@interface STPreviewsViewItem : NSObject

- (id)initWithUser:(id<STUser>)user icon:(UIImage*)icon action:(id<STAction>)action andContext:(STActionContext*)context;

@property (nonatomic, readonly, retain) id<STUser> user;
@property (nonatomic, readonly, retain) UIImage* icon;
@property (nonatomic, readonly, retain) STActionPair* pair;

@end

@implementation STPreviewsViewItem

@synthesize user = user_;
@synthesize icon = icon_;
@synthesize pair = pair_;

- (id)initWithUser:(id<STUser>)user icon:(UIImage*)icon action:(id<STAction>)action andContext:(STActionContext*)context {
  self = [super init];
  if (self) {
    user_ = [user retain];
    icon_ = [icon retain];
    pair_ = [[STActionPair actionPairWithAction:action andContext:context] retain];
  }
  return self;
}

- (void)dealloc
{
  [user_ release];
  [icon_ release];
  [pair_ release];
  [super dealloc];
}

@end

@interface STPreviewsView ()

@property (nonatomic, readonly, retain) NSMutableArray* items;

@end

@implementation STPreviewsView

static const CGFloat _cellWidth = 35;
static const CGFloat _cellHeight = 35;
static const NSInteger _cellsPerRow = 7;

@synthesize items = items_;

+ (NSInteger)totalItemsForPreviews:(id<STPreviews>)previews {
  if (previews) {
      return previews.credits.count + previews.likes.count + previews.todos.count; //+ previews.comments.count;
  }
  return 0;
}

+ (NSInteger)totalRowsForPreviews:(id<STPreviews>)previews andMaxRows:(NSInteger)maxRows {
  NSInteger itemsCount = [STPreviewsView totalItemsForPreviews:previews];
  NSInteger rows = itemsCount / _cellsPerRow;
  rows += itemsCount % _cellsPerRow ? 1 : 0;
  return MIN(maxRows,rows);
}

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        self.backgroundColor = [UIColor whiteColor];
    }
    return self;
}

- (void)setupWithPreview:(id<STPreviews>)previews maxRows:(NSInteger)maxRows {
    
    [self.subviews makeObjectsPerformSelector:@selector(removeFromSuperview)];
        
    UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"inbox_cell_dash.png"]];
    [self addSubview:imageView];
    
    CGRect frame = imageView.frame;
    frame.origin.y -= 8.0f;
    imageView.frame = frame;
    [imageView release];

    NSInteger total = [STPreviewsView totalItemsForPreviews:previews];
    if (total > 0) {
        NSInteger numberOfRows = [STPreviewsView totalRowsForPreviews:previews andMaxRows:maxRows];
        CGFloat height = numberOfRows * _cellHeight;
        self.frame = CGRectMake(self.frame.origin.x, self.frame.origin.y, _cellWidth * MIN(_cellsPerRow, total), height);
        NSInteger limit = MIN(_cellsPerRow * numberOfRows, total);
        BOOL continuedFlag = NO;
        if (limit < total) {
            // TODO add support for continued button
            continuedFlag = YES;
        }
        items_ = [[NSMutableArray alloc] init];
        for (id<STStamp> credit in previews.credits) {
            if (items_.count < limit) {
                UIImage* image = [Util stampImageForUser:credit.user withSize:STStampImageSize12];
                STActionContext* context = [STActionContext context];
                id<STAction> action = [STStampedActions actionViewStamp:credit.stampID withOutputContext:context];
                STPreviewsViewItem* item = [[[STPreviewsViewItem alloc] initWithUser:credit.user icon:image action:action andContext:context] autorelease];
                [items_ addObject:item];
            }
            else {
                break;
            }
        }
        UIImage* likeIcon = [UIImage imageNamed:@"like_mini"];
        for (id<STUser> like in previews.likes) {
            if (items_.count < limit) {
                STActionContext* context = [STActionContext context];
                context.user = like;
                id<STAction> action = [STStampedActions actionViewUser:like.userID withOutputContext:context];
                STPreviewsViewItem* item = [[[STPreviewsViewItem alloc] initWithUser:like icon:likeIcon action:action andContext:context] autorelease];
                [items_ addObject:item];
            }
            else {
                break;
            }
        }
        UIImage* todoIcon = [UIImage imageNamed:@"todo_mini"];
        for (id<STUser> todo in previews.todos) {
            if (items_.count < limit) {
                STActionContext* context = [STActionContext context];
                context.user = todo;
                id<STAction> action = [STStampedActions actionViewUser:todo.userID withOutputContext:context];
                STPreviewsViewItem* item = [[[STPreviewsViewItem alloc] initWithUser:todo icon:todoIcon action:action andContext:context] autorelease];
                [items_ addObject:item];
            }
            else {
                break;
            }
        }
        /*
        UIImage* commentIcon = [UIImage imageNamed:@"comment_mini"];
        for (id<STComment> comment in previews.comments) {
            if (items_.count < limit) {
                STActionContext* context = [STActionContext context];
                context.user = comment.user;
                id<STAction> action = [STStampedActions actionViewUser:comment.user.userID withOutputContext:context];
                STPreviewsViewItem* item = [[[STPreviewsViewItem alloc] initWithUser:comment.user icon:commentIcon action:action andContext:context] autorelease];
                [items_ addObject:item];
            }
            else {
                break;
            }
        }
         */
        for (NSInteger i = limit - 1; i >= 0; i--) {
            NSInteger col = i % _cellsPerRow;
            NSInteger row = i / _cellsPerRow;
            CGFloat xOffset = col * _cellWidth;
            CGFloat yOffset = row * _cellHeight;
            if (i == limit - 1 && continuedFlag) {
                UIView* box = [[[UIView alloc] initWithFrame:CGRectMake(xOffset, yOffset, 31, 31)] autorelease];
                box.backgroundColor = [UIColor colorWithWhite:.85 alpha:1];
                box.layer.borderColor = [UIColor whiteColor].CGColor;
                box.layer.borderWidth = 1;
                UIView* dots = [Util viewWithText:@"..." 
                                             font:[UIFont stampedBoldFontWithSize:20]
                                            color:[UIColor stampedGrayColor]
                                             mode:UILineBreakModeClip
                                       andMaxSize:CGSizeMake(31, 31)];
                dots.frame = [Util centeredAndBounded:dots.frame.size inFrame:CGRectMake(0, 0, 31, 31)];
                [box addSubview:dots];
                [self addSubview:box];
            }
            else {
                STPreviewsViewItem* item = [items_ objectAtIndex:i];
                UIView* userImage = [Util profileImageViewForUser:item.user withSize:STProfileImageSize31];
                userImage.layer.shadowOpacity = 0.1f;
                userImage.layer.shadowRadius = 1.5f;
                [Util reframeView:userImage withDeltas:CGRectMake(xOffset, yOffset, 0, 0)];
                [self addSubview:userImage];
                UIImageView* imageView = [[[UIImageView alloc] initWithImage:item.icon] autorelease];
                [Util reframeView:imageView withDeltas:CGRectMake(xOffset + userImage.frame.size.width * .6, yOffset + userImage.frame.size.height * .6, 0, 0)];
                [self addSubview:imageView];
                //UIView* button = [Util tapViewWithFrame:CGRectMake(xOffset, yOffset, _cellWidth, _cellHeight) target:self selector:@selector(previewClicked:) andMessage:item];
                //[self addSubview:button];
            }
        }
        for (NSInteger i = limit - 1; i >= 0; i--) {
            NSInteger col = i % _cellsPerRow;
            NSInteger row = i / _cellsPerRow;
            CGFloat xOffset = col * _cellWidth;
            CGFloat yOffset = row * _cellHeight;
            CGFloat padding = 5;
            if (i == limit - 1 && continuedFlag) {
            }
            else {
                STPreviewsViewItem* item = [items_ objectAtIndex:i];
                CGRect buttonFrame = CGRectMake(xOffset-padding, yOffset-padding, 31+ 2*padding, 31+ 2*padding);
                CGRect viewFrame = CGRectMake(0, 0, buttonFrame.size.width, buttonFrame.size.height);
                UIView* activeView = [[[UIView alloc] initWithFrame:viewFrame] autorelease];
                activeView.backgroundColor = [UIColor colorWithRed:0 green:0 blue:.3 alpha:.3];
                activeView.layer.cornerRadius = padding;
                STButton* button = [[[STButton alloc] initWithFrame:buttonFrame 
                                                         normalView:[[[UIView alloc] initWithFrame:viewFrame] autorelease]
                                                         activeView:activeView
                                                             target:item.pair
                                                          andAction:@selector(executeActionWithArg:)] autorelease];
                [self addSubview:button];
            }
        }
    }

    
}

- (void)setupWithStamp:(id<STStamp>)stamp maxRows:(NSInteger)maxRows {
    [self setupWithPreview:stamp.previews maxRows:maxRows];
}

- (void)dealloc {
  [items_ release];
  [super dealloc];
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
    BOOL continuedFlag = NO;
    if (limit < total) {
      // TODO add support for continued button
      continuedFlag = YES;
    }
    
    for (id<STStamp> credit in previews.credits) {
      if (images.count < limit) {
        [images addObject:[Util profileImageURLForUser:credit.user withSize:STProfileImageSize31]];
      }
      else {
        break;
      }
    }
    for (id<STUser> like in previews.likes) {
      if (images.count < limit) {
        [images addObject:[Util profileImageURLForUser:like withSize:STProfileImageSize31]];
      }
      else {
        break;
      }
    }
    for (id<STUser> todo in previews.todos) {
      if (images.count < limit) {
        [images addObject:[Util profileImageURLForUser:todo withSize:STProfileImageSize31]];
      }
      else {
        break;
      }
    }
      /*
    for (id<STComment> comment in previews.comments) {
      if (images.count < limit) {
        [images addObject:[Util profileImageURLForUser:comment.user withSize:STProfileImageSize31]];
      }
      else {
        break;
      }
    }
       */
  }
  return images;
}

@end
