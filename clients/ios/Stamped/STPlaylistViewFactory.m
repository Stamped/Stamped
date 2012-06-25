//
//  STPlaylistViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 4/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STPlaylistViewFactory.h"
#import "STViewContainer.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import <QuartzCore/QuartzCore.h>

@interface STPlaylistItemView : UIView

- (id)initWithPlaylistItem:(id<STPlaylistItem>)playlistItem 
              entityDetail:(id<STEntityDetail>)entityDetail 
                     index:(NSInteger)index
               andDelegate:(id<STViewDelegate>)delegate;

- (void)viewEntity:(id)message;
- (void)play:(id)message;

@property (nonatomic, readonly, retain) id<STPlaylistItem> playlistItem;
@property (nonatomic, readonly, retain) id<STEntityDetail> entityDetail;

@end

@implementation STPlaylistItemView

@synthesize playlistItem = _playlistItem;
@synthesize entityDetail = _entityDetail;

- (id)initWithPlaylistItem:(id<STPlaylistItem>)playlistItem 
              entityDetail:(id<STEntityDetail>)entityDetail 
                     index:(NSInteger)index
               andDelegate:(id<STViewDelegate>)delegate {
    self = [super initWithFrame:CGRectMake(0, 0, 290, 50)];
    if (self) {
        _playlistItem = [playlistItem retain];
        _entityDetail = [entityDetail retain];
        if (playlistItem.entityID) {
            UIView* button = [Util tapViewWithFrame:self.frame target:self selector:@selector(viewEntity:) andMessage:nil];
            [self addSubview:button];
        }
        UIView* nameView = [Util viewWithText: playlistItem.name ? playlistItem.name : @"?"
                                         font:[UIFont stampedFontWithSize:16]
                                        color:playlistItem.entityID ? [UIColor stampedLinkColor] : [UIColor stampedDarkGrayColor]
                                         mode:UILineBreakModeTailTruncation
                                   andMaxSize:CGSizeMake(180, 40)];
        nameView.frame = [Util centeredAndBounded:nameView.frame.size inFrame:CGRectMake(65, 5, nameView.frame.size.width, 40)];
        [self addSubview:nameView];
        UIView* indexView = [Util viewWithText:[NSString stringWithFormat:@"%d.",index+1]
                                          font:[UIFont stampedFontWithSize:16]
                                         color:[UIColor stampedGrayColor]
                                          mode:UILineBreakModeTailTruncation
                                    andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
        indexView.frame = [Util centeredAndBounded:indexView.frame.size 
                                           inFrame:CGRectMake(self.frame.size.height-10, 5, indexView.frame.size.width, 40)];
        [self addSubview:indexView];
        if (playlistItem.action) {
            STActionContext* context = [STActionContext contextInView:self];
            context.entityDetail = entityDetail;
            if ([[STActionManager sharedActionManager] canHandleAction:playlistItem.action withContext:context]) {
                UIImageView* playIcon = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"act_play_primary"]] autorelease];
                playIcon.frame = [Util centeredAndBounded:playIcon.frame.size inFrame:CGRectMake(0, 0, self.frame.size.height, self.frame.size.height)];
                [self addSubview:playIcon];
                UIView* playButton = [Util tapViewWithFrame:CGRectMake(0, 0, self.frame.size.height, self.frame.size.height) 
                                                     target:self 
                                                   selector:@selector(play:) 
                                                 andMessage:nil];
                [self addSubview:playButton];
            }
        }
        if (playlistItem.length != 0) {
            UIView* lengthView = [Util viewWithText:[Util trackLengthString:playlistItem.length]
                                               font:[UIFont stampedFontWithSize:16] 
                                              color:[UIColor stampedGrayColor]
                                               mode:UILineBreakModeTailTruncation 
                                         andMaxSize:CGSizeMake(50, 40)];
            lengthView.frame = [Util centeredAndBounded:lengthView.frame.size 
                                                inFrame:CGRectMake(240, 0, lengthView.frame.size.width, self.frame.size.height)];
            [self addSubview:lengthView];
        }
    }
    return self;
}

- (void)dealloc
{
    [_playlistItem release];
    [_entityDetail release];
    [super dealloc];
}

- (void)viewEntity:(id)message {
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewEntity:self.playlistItem.entityID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)play:(id)message {
    STActionContext* context = [STActionContext contextInView:self];
    context.entityDetail = self.entityDetail;
    [[STActionManager sharedActionManager] didChooseAction:self.playlistItem.action withContext:context];
}

@end

@interface STPlaylistView : STViewContainer

- (id)initWithEntityDetail:(id<STEntityDetail>)entityDetail andDelegate:(id<STViewDelegate>)delegate;

@end

@implementation STPlaylistView

- (id)initWithEntityDetail:(id<STEntityDetail>)entityDetail andDelegate:(id<STViewDelegate>)delegate {
    self = [super initWithFrame:CGRectMake(15, 0, 290, 0)];
    if (self) {
        if ([entityDetail.playlist.data count] > 0) {
            
            self.layer.cornerRadius = 2.0;
            self.layer.borderColor =[UIColor colorWithRed:.8 green:.8 blue:.8 alpha:.4].CGColor;
            self.layer.borderWidth = 1.0;
            self.layer.shadowColor = [UIColor blackColor].CGColor;
            self.layer.shadowOpacity = .05;
            self.layer.shadowRadius = 1.0;
            self.layer.shadowOffset = CGSizeMake(0, 1);
            
            if (entityDetail.playlist.name) {
                UIView* titleView = [Util viewWithText:entityDetail.playlist.name 
                                                  font:[UIFont stampedBoldFontWithSize:16] 
                                                 color:[UIColor stampedDarkGrayColor] 
                                                  mode:UILineBreakModeTailTruncation
                                            andMaxSize:CGSizeMake(self.frame.size.width, CGFLOAT_MAX)];
                [Util reframeView:titleView withDeltas:CGRectMake(10, 0, 0, 10)];
                [self appendChildView:titleView];
            }
            UIImage* image = [UIImage imageNamed:@"eDetailBox_line"];
            NSInteger index = 0;
            for (id<STPlaylistItem> item in entityDetail.playlist.data) {
                if (index != 0) {
                    UIImageView* barView = [[[UIImageView alloc] initWithImage:image] autorelease];
                    [self appendChildView:barView];
                }
                STPlaylistItemView* itemView = [[[STPlaylistItemView alloc] initWithPlaylistItem:item 
                                                                                    entityDetail:entityDetail 
                                                                                           index:index
                                                                                     andDelegate:self] autorelease];
                [self appendChildView:itemView];
                index++;
            }
            [Util addGradientToLayer:self.layer withColors:[UIColor stampedLightGradient] vertical:YES];
        }
    }
    return self;
}

@end

@implementation STPlaylistViewFactory

- (id)generateAsynchronousState:(id<STEntityDetail>)anEntityDetail withOperation:(NSOperation*)operation {
    return nil;
}

- (UIView*)generateViewOnMainLoop:(id<STEntityDetail>)anEntityDetail
                        withState:(id)asyncState
                      andDelegate:(id<STViewDelegate>)delegate {
    return [[[STPlaylistView alloc] initWithEntityDetail:anEntityDetail andDelegate:delegate] autorelease];
}

@end
