//
//  STNewStampCell.m
//  Stamped
//
//  Created by Landon Judkins on 7/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STNewStampCell.h"
#import "STUserImageView.h"
#import "Util.h"
#import "STChunksView.h"
#import "STPreviewsView.h"

//Unfinished

static const CGFloat _yAdjustment = 0;

@interface STNewStampCell ()

@property (nonatomic, readonly, retain) STUserImageView* userImageView;
@property (nonatomic, readonly, retain) UIImageView* stampImageView;
@property (nonatomic, readwrite, retain) STChunksView* chunksView;
@property (nonatomic, readonly, retain) STPreviewsView* previewsView;

@end

@implementation STNewStampCell

@synthesize userImageView = _userImageView;
@synthesize stampImageView = _stampImageView;

@synthesize chunksView = _chunksView;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier
{
    self = [super initWithStyle:style reuseIdentifier:reuseIdentifier];
    if (self) {
        _userImageView = [[STUserImageView alloc] initWithSize:48];
        [Util reframeView:_userImageView withDeltas:CGRectMake(11, 10 + _yAdjustment, 0, 0)];
        [self.contentView addSubview:_userImageView];
        _stampImageView = [[UIImageView alloc] initWithFrame:CGRectMake(0, 26 + _yAdjustment, 18, 18)];
        [self.contentView addSubview:_stampImageView];
    }
    return self;
}

- (void)dealloc
{
    [_userImageView release];
    [_stampImageView release];
    [super dealloc];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated
{
    [super setSelected:selected animated:animated];
}

- (void)setupWithStamp:(id<STStamp>)stamp {
    
}

+ (CGFloat)heightForStamp:(id<STStamp>)stamp {
    
}

@end
