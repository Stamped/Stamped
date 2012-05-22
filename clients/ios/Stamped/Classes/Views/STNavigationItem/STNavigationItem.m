//
//  GiftureNavigationItem.m
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import "STNavigationItem.h"
#import "STNavigationButton.h"

@implementation STNavigationItem

- (UIImage*)imageForBarButtonItemType:(UIBarButtonSystemItem)itemType{
		
	switch (itemType) {
        case UIBarButtonSystemItemCompose:
            return [UIImage imageNamed:@"navigation_compose_button.png"];
            break;
		case UIBarButtonSystemItemAction:
			return [UIImage imageNamed:@"navigation_action_button.png"];
			break;
		case UIBarButtonSystemItemAdd:
			return [UIImage imageNamed:@"navigation_add_button.png"];
			break;
		case UIBarButtonSystemItemReply:
			return [UIImage imageNamed:@"navigation_reply_button.png"];
			break;
		default:
			break;
	}
	
	return nil;
	
}

- (id)initWithImage:(UIImage *)image style:(UIBarButtonItemStyle)style target:(id)target action:(SEL)action {
	
	STNavigationButton *button = [STNavigationButton buttonWithImage:image buttonStyle:style];
    [button setImage:image forState:UIControlStateHighlighted];
	[button addTarget:target action:action forControlEvents:UIControlEventTouchUpInside];
	
	if ((self = [super initWithCustomView:button])) {
		
	}
	
	return self;
	
}

- (id)initWithBackButtonTitle:(NSString *)title style:(UIBarButtonItemStyle)style target:(id)target action:(SEL)action {
	
	
	//_doneStyle = (style == UIBarButtonItemStyleDone);
	
	STNavigationButton *button = [STNavigationButton backButtonWithTitle:title];
	[button addTarget:target action:action forControlEvents:UIControlEventTouchUpInside];	
	if ((self = [super initWithCustomView:button])) {
		
		
	}
	
	return self;
	
}

- (id)initWithTitle:(NSString *)title style:(UIBarButtonItemStyle)style target:(id)target action:(SEL)action{
	
	STNavigationButton *button = [STNavigationButton buttonWithTitle:title buttonStyle:style];
	[button addTarget:target action:action forControlEvents:UIControlEventTouchUpInside];	
	if ((self = [super initWithCustomView:button])) {
		
		
	}
	
	return self;
	
}

- (id)initWithBarButtonSystemItem:(UIBarButtonSystemItem)systemItem target:(id)target action:(SEL)action{
	
	STNavigationButton *button = [STNavigationButton buttonWithImage:[self imageForBarButtonItemType:systemItem] buttonStyle:UIBarButtonItemStyleBordered];
	[button addTarget:target action:action forControlEvents:UIControlEventTouchUpInside];
	
	if ((self = [super initWithCustomView:button])) {
		
		
	}
	
	return self;
	
}

- (void)setTitle:(NSString *)aTitle{
	
	if (self.customView && [self.customView isKindOfClass:[UIButton class]]) {
		UIButton *button = (UIButton*)self.customView;
		[button setTitle:aTitle forState:UIControlStateNormal];
	}
	
}


@end
