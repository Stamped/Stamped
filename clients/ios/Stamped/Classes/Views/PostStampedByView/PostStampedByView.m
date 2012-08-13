//
//  PostStampedByView.m
//  Stamped
//
//  Created by Devin Doty on 6/17/12.
//
//

#import "PostStampedByView.h"
#import "STTableViewSectionBackground.h"
#import "STAvatarView.h"
#import "STStampedAPI.h"
#import "Util.h"

#define kPostStampedByMaxHeight 100.0f
#define kStampedByCellWidth 39.0f

@interface PostStampedByView ()

@end

@implementation PostStampedByView

@synthesize stampedBy=_stampedBy;
@synthesize titleLabel=_titleLabel;
@synthesize delegate;

- (void)commonInit {
    
    STTableViewSectionBackground *view = [[STTableViewSectionBackground alloc] initWithFrame:CGRectInset(self.bounds, 10, 2)];
    view.backgroundColor = [UIColor clearColor];
    view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    [self addSubview:view];
    [view release];
    
    UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stamped_by_globe.png"]];
    [self addSubview:imageView];
    
    CGRect frame = imageView.frame;
    frame.origin.x = 34.0f;
    frame.origin.y = 15.0f;
    imageView.frame = frame;
    [imageView release];

    UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
    label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
    label.backgroundColor = [UIColor clearColor];
    label.font = [UIFont systemFontOfSize:11];
    [self addSubview:label];
    _titleLabel = [label retain];
    [label release];
    
    UIView *contentView = [[UIView alloc] initWithFrame:CGRectMake(28.0f, 32.0f, self.bounds.size.width-56.0f, kStampedByCellWidth)];
    [self addSubview:contentView];
    _contentView = contentView;
    [contentView release];
    
    NSInteger count = floorf(contentView.bounds.size.width / kStampedByCellWidth);
    
    NSMutableArray *views = [[NSMutableArray alloc] initWithCapacity:count];
    for (NSInteger i = 0; i < count; i++) {
        STAvatarView *view = [[STAvatarView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, kStampedByCellWidth, kStampedByCellWidth)];
        view.delegate = (id<STAvatarViewDelegate>)self;
        view.hidden = YES;
        [view setDefault];
        [_contentView addSubview:view];
        [views addObject:view];
        [view release];
    }
    
    _views = [views retain];
    [views release];
    
    UIImage *image = [UIImage imageNamed:@"stamped_by_arrow.png"];
    UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
    [button setImage:image forState:UIControlStateNormal];
    [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
    [_contentView addSubview:button];
    _button = button;
    _button.hidden = YES;
    
    frame = button.frame;
    frame.size = image.size;
    frame.origin.y = floorf(((_contentView.bounds.size.height-image.size.height)/2) + 1.0f);
    button.frame = frame;

}

//- (id)initWithFrame:(CGRect)frame entityIdentifier:(NSString*)entityIdentifier {
//    if ((self = [super initWithFrame:frame])) {
//        [self commonInit];
//        [[STStampedAPI sharedInstance] stampedByForEntityID:entityIdentifier andCallback:^(id<STStampedBy> stampedBy, NSError *error, STCancellation *cancellation) {
//            self.stampedBy = stampedBy;
//
//        }];
//    }
//    return self;
//    
//}
//
//- (id)initWithFrame:(CGRect)frame stampedBy:(id<STStampedBy>)stampedBy {
//    if ((self = [super initWithFrame:frame])) {
//        [self commonInit];
//        self.stampedBy = stampedBy;
//    }
//    return self;
//}
//
//- (id)initWithFrame:(CGRect)frame {
//    if ((self = [super initWithFrame:frame])) {
//        [self commonInit];
//    }
//    return self;
//}

- (id)init {
    self = [super initWithFrame:CGRectMake(0.0f, 0., [Util fullscreenFrame].size.width, 85.0f)];
    if (self) {
        [self commonInit];
    }
    return self;
}

- (void)dealloc {
    
    self.delegate = nil;
    [_views release], _views=nil;
    [_titleLabel release], _titleLabel=nil;
    [_stampedBy release], _stampedBy=nil;
    [super dealloc];
}


#pragma mark - Layout

- (void)layoutSubviews {
    [super layoutSubviews];
    
    CGFloat originX = 0.0f;
    CGRect frame;
    for (UIView *view in _views) {
        
        if (!view.hidden) {
            frame = view.frame;
            frame.origin.x = originX;
            originX += (kStampedByCellWidth - 1.5f);
            view.frame = frame;
        }
        
    }
    
    if (!_button.hidden) {
        frame = _button.frame;
        frame.origin.x = originX + 3.0f;
        _button.frame = frame;
    }
    
    [_titleLabel sizeToFit];
    frame = _titleLabel.frame;
    frame.origin.x = 58.0f;
    frame.origin.y = 15.0f;
    _titleLabel.frame = frame;
    
    
}


#pragma mark - Setters

- (NSInteger)setupWithGroup:(id<STStampedByGroup>)group count:(NSInteger)count cap:(BOOL)cap {
    
    for (NSInteger i = 0; i < group.stampPreviews.count && i < _views.count; i++) {
        
        STAvatarView *view = [_views objectAtIndex:count];
        id <STStampPreview> preview = [[group stampPreviews] objectAtIndex:i];
        view.imageURL = [NSURL URLWithString:preview.user.imageURL];
        view.calloutTitle = preview.user.screenName;
        view.hidden = NO;
        count++;
        if (cap && count == [_views count]) {
            return count;
        }
        
    }
    
    return count;
    
}

- (void)setStampedBy:(id<STStampedBy>)stampedBy {
    [_stampedBy release], _stampedBy=nil;
    _stampedBy = [stampedBy retain];
    
    NSInteger filled = 0;
    NSInteger maxCount = stampedBy.everyone.count.integerValue; //+ stampedBy.friends.count.integerValue;
    
    BOOL cap = maxCount > 7;
    //filled += [self setupWithGroup:stampedBy.friends count:filled cap:cap];
    filled += [self setupWithGroup:stampedBy.everyone count:filled cap:cap];

    if (maxCount>7) {
        _button.hidden = NO;
    }
    
    _titleLabel.text = [NSString stringWithFormat:@"Also stamped by %i other user%@", maxCount, maxCount==1 ? @"" : @"s"];
    [self setNeedsLayout];
    
}


#pragma mark - Actions

- (void)buttonHit:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(postStampedByView:selectedAll:)]) {
        [self.delegate postStampedByView:self selectedAll:sender];
    }

}


#pragma mark - STAvatarViewDelegate

- (void)stAvatarViewTapped:(STAvatarView*)view {
    
    if ([(id)delegate respondsToSelector:@selector(postStampedByView:selectedPreview:)]) {

        NSInteger index = [_views indexOfObject:view];
        
        if (index!=NSNotFound) {
            
            id <STStampPreview> preview = [[self.stampedBy.everyone stampPreviews] objectAtIndex:index];
            [self.delegate postStampedByView:self selectedPreview:preview];

            /*
            
            if (index < self.stampedBy.friends.count.integerValue) {
                
                id <STStampPreview> preview = [[self.stampedBy.friends stampPreviews] objectAtIndex:index];
                [self.delegate postStampedByView:self selectedPreview:preview];
                
            } else {
                
                index += self.stampedBy.friends.count.integerValue;
                id <STStampPreview> preview = [[self.stampedBy.everyone stampPreviews] objectAtIndex:index];
                [self.delegate postStampedByView:self selectedPreview:preview];

            }
             */
        }
    }
    
}

@end
