//
//  STBadgeBarButtonItem.m
//  Stamped
//
//  Created by Devin Doty on 6/8/12.
//
//

#import "STBadgeBarButtonItem.h"
#import "STNavigationItem.h"

@implementation STBadgeBarButtonItem

- (id)initWithImage:(UIImage *)image style:(UIBarButtonItemStyle)style target:(id)target action:(SEL)action {
    if (self = [super initWithImage:image style:style target:target action:action]) {
        [STEvents addObserver:self selector:@selector(countUpdated:) event:EventTypeUnreadCountUpdated];
    }
    return self;
}

- (void)dealloc {
    [STEvents removeObserver:self];
    [super dealloc];
}


#pragma mark - Notifications 

- (void)countUpdated:(NSNotification*)notification {
    if (![notification object]) return;
    
    if ([[notification object] integerValue] > 0) {
        
        if (!_countView) {
            UIView *countView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 19, 19)] autorelease];
            countView.userInteractionEnabled = NO;
            UILabel *label = [Util viewWithText:[NSString stringWithFormat:@"%d", [[notification object] integerValue]]
                                           font:[UIFont boldSystemFontOfSize:10]
                                          color:[UIColor whiteColor]
                                           mode:UILineBreakModeTailTruncation
                                     andMaxSize:countView.frame.size];
            label.frame = CGRectMake(ceilf((countView.bounds.size.width-label.bounds.size.width)/2), floorf((countView.bounds.size.height-label.bounds.size.height)/2), label.bounds.size.width, label.bounds.size.height);
            label.userInteractionEnabled = NO;
            label.shadowOffset = CGSizeMake(0.0f, -1.0f);
            label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.2f];
            [countView addSubview:label];

            [Util reframeView:countView withDeltas:CGRectMake(26, -5, 0, 0)];
            countView.layer.borderWidth = 1;
            countView.layer.borderColor = [UIColor whiteColor].CGColor;
            countView.layer.cornerRadius = countView.frame.size.width / 2;
            countView.layer.shadowPath = [UIBezierPath bezierPathWithRoundedRect:countView.bounds cornerRadius:(countView.bounds.size.width/2)].CGPath;
            countView.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
            countView.layer.shadowRadius = 2.0f;
            countView.layer.shadowOpacity = 0.4f;
            
            CAGradientLayer *layer = [Util addGradientToLayer:countView.layer
                                                   withColors:[NSArray arrayWithObjects:
                                                               [UIColor colorWithRed:0.890f green:0.364f blue:0.2588f alpha:1.0f],
                                                               [UIColor colorWithRed:0.717f green:0.207f blue:0.1019f alpha:1.0f],
                                                               nil]
                                                     vertical:YES];
            CGRect frame = layer.frame;
            frame = CGRectInset(frame, .5, .5);
            layer.frame = frame;
            
            [self.customView addSubview:countView];
            _countView = countView;
            _countLabel = label;
        }
       
        _countLabel.text = [NSString stringWithFormat:@"%d", [[notification object] integerValue]];
        [_countLabel sizeToFit];
        _countLabel.frame = CGRectMake(ceilf((_countView.bounds.size.width-_countLabel.bounds.size.width)/2), floorf((_countView.bounds.size.height-_countLabel.bounds.size.height)/2), _countLabel.bounds.size.width, _countLabel.bounds.size.height);

    } else {
    
        if  (_countView) {
            [_countView removeFromSuperview], _countView=nil;
        }
    
    }

}

@end
